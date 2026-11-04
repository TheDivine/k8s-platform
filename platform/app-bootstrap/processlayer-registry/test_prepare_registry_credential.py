"""Offline credential-boundary regressions; no real PAT or network is used."""
import base64
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request
import warnings

import yaml

SPEC = importlib.util.spec_from_file_location("registry_helper", Path(__file__).with_name("prepare_registry_credential.py"))
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)
ROOT = Path(__file__).resolve().parents[3]
DUMMY = "fixture-only-not-a-real-credential"


def sealed_fixture():
    encrypted = base64.b64encode((256).to_bytes(2, "big") + b"X" * (256 + 32)).decode()
    metadata = {"name": helper.NAME, "namespace": helper.NAMESPACE, "creationTimestamp": None}
    return {"apiVersion": "bitnami.com/v1alpha1", "kind": "SealedSecret", "metadata": metadata,
            "spec": {"encryptedData": {".dockerconfigjson": encrypted},
                     "template": {"metadata": metadata.copy(), "type": helper.SECRET_TYPE}}}


class AccessTests(unittest.TestCase):
    def request(self, method, url, headers):
        self.calls.append((method, url))
        self.assertIn((method, url), helper.ALLOWED_REQUESTS)
        if url == helper.API_URL:
            self.assertEqual(headers["Authorization"], "Bearer " + DUMMY)
            return json.dumps({"login": self.owner}).encode(), {"x-oauth-scopes": self.scopes}
        if method == "GET":
            expected = base64.b64encode((helper.OWNER + ":" + DUMMY).encode()).decode()
            self.assertEqual(headers["Authorization"], "Basic " + expected)
            return b'{"token":"fixture-registry-bearer"}', {}
        self.assertEqual(headers["Authorization"], "Bearer fixture-registry-bearer")
        image = next(image for image in helper.IMAGES if url == helper.manifest_url(image))
        return b"", {"docker-content-digest": self.digest_override or helper.IMAGES[image]}

    def setUp(self):
        self.owner = helper.OWNER
        self.scopes = "read:packages"
        self.digest_override = None
        self.calls = []

    def test_exact_owner_scope_and_all_three_pinned_manifests(self):
        auth = helper.verify_access(DUMMY, self.request)
        self.assertEqual(base64.b64decode(auth).decode(), helper.OWNER + ":" + DUMMY)
        self.assertEqual(len(self.calls), 7)
        self.assertEqual({url for method, url in self.calls if method == "HEAD"},
                         {helper.manifest_url(image) for image in helper.IMAGES})

    def test_missing_broader_or_wrong_owner_stops_before_registry(self):
        for owner, scopes in (("another-owner", "read:packages"), (helper.OWNER, ""),
                              (helper.OWNER, "repo, read:packages"),
                              (helper.OWNER, "write:packages, read:packages"),
                              (helper.OWNER, "read:packages, delete:packages")):
            with self.subTest(owner=owner, scopes=scopes):
                self.owner, self.scopes, self.calls = owner, scopes, []
                with self.assertRaises(helper.SafeFailure):
                    helper.verify_access(DUMMY, self.request)
                self.assertEqual(self.calls, [("GET", helper.API_URL)])

    def test_manifest_mismatch_or_registry_denial_blocks_output(self):
        self.digest_override = "sha256:" + "0" * 64
        with self.assertRaises(helper.SafeFailure):
            helper.verify_access(DUMMY, self.request)
        self.assertEqual(len(self.calls), 3)
        with self.assertRaises(helper.SafeFailure):
            helper.verify_access(DUMMY, lambda *args: (_ for _ in ()).throw(helper.SafeFailure("Denied")))

    def test_transport_refuses_redirects_unexpected_endpoints_and_response_details(self):
        self.assertIsNone(helper.NoRedirect().redirect_request(None, None, 302, None, None, "https://other.invalid"))
        with self.assertRaises(helper.SafeFailure):
            helper.fetch("GET", "https://other.invalid/", {})
        error = urllib.error.HTTPError(helper.API_URL, 403, DUMMY, {}, io.BytesIO(DUMMY.encode()))
        with patch.object(urllib.request.OpenerDirector, "open", side_effect=error):
            with self.assertRaises(helper.SafeFailure) as caught:
                helper.fetch("GET", helper.API_URL, {"Authorization": "Bearer " + DUMMY})
        self.assertNotIn(DUMMY, str(caught.exception))

    def test_hidden_prompt_must_not_fall_back_to_echo(self):
        def no_terminal(*args):
            warnings.warn("No terminal", helper.getpass.GetPassWarning)
            self.fail("getpass fallback must be interrupted before reading echoed stdin")
        with patch.object(helper.getpass, "getpass", side_effect=no_terminal):
            with self.assertRaises(helper.SafeFailure):
                helper.read_token()
        with patch.object(helper.getpass, "getpass", return_value="github_pat_fixture"):
            with self.assertRaises(helper.SafeFailure):
                helper.read_token()


class PreparationTests(unittest.TestCase):
    def test_sealed_contract_rejects_scope_plaintext_wrong_owner_and_extra_fields(self):
        helper.validate_sealed(sealed_fixture())
        changes = (
            lambda value: value.update(data={"fixture": DUMMY}),
            lambda value: value["spec"]["template"].update(stringData={"fixture": DUMMY}),
            lambda value: value["metadata"].update(annotations={"sealedsecrets.bitnami.com/cluster-wide": "true"}),
            lambda value: value["spec"]["template"]["metadata"].update(namespace="processlayer"),
            lambda value: value["metadata"].update(name="ghcr-pull"),
            lambda value: value["spec"]["template"].update(type="Opaque"),
            lambda value: value["spec"]["encryptedData"].update({".dockerconfigjson": base64.b64encode(DUMMY.encode()).decode()}),
            lambda value: value["spec"].update(extra=DUMMY),
        )
        for change in changes:
            value = copy.deepcopy(sealed_fixture())
            change(value)
            with self.assertRaises(helper.SafeFailure):
                helper.validate_sealed(value)

    def test_only_ciphertext_written_and_plaintext_uses_stdin_not_arguments(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            cert = folder / "public.pem"
            cert.write_text("-----BEGIN CERTIFICATE-----\nfixture-public-only\n")
            seen = []
            def command(args, payload=None):
                self.assertNotIn(DUMMY, " ".join(args))
                seen.append(args)
                if args[0] == "openssl":
                    self.assertIsNone(payload)
                    return b""
                self.assertEqual(args, ["kubeseal", "--cert", str(cert.resolve()), "--scope", "strict", "--format", "json"])
                secret = json.loads(payload)
                self.assertEqual(secret["metadata"], {"name": helper.NAME, "namespace": "processlayer-prod"})
                self.assertEqual(secret["type"], helper.SECRET_TYPE)
                config = json.loads(base64.b64decode(secret["data"][".dockerconfigjson"]))
                self.assertEqual(set(config["auths"]), {"ghcr.io"})
                self.assertEqual(base64.b64decode(config["auths"]["ghcr.io"]["auth"]).decode(), helper.OWNER + ":" + DUMMY)
                return json.dumps(sealed_fixture()).encode()
            auth = base64.b64encode((helper.OWNER + ":" + DUMMY).encode()).decode()
            with patch.object(helper, "command", side_effect=command), patch.object(helper, "read_token", return_value=DUMMY), patch.object(helper, "verify_access", return_value=auth):
                output = helper.prepare(cert, folder)
            self.assertEqual({path.name for path in folder.iterdir()}, {"public.pem", helper.SEALED_FILE})
            self.assertNotIn(DUMMY, output.read_text())
            self.assertNotIn(auth, output.read_text())
            helper.validate_sealed(json.loads(output.read_text()))
            self.assertEqual([args[0] for args in seen], ["openssl", "kubeseal"])

    def test_staging_uses_separate_ciphertext_and_strict_namespace(self):
        value = sealed_fixture()
        value["metadata"]["namespace"] = "processlayer"
        value["spec"]["template"]["metadata"]["namespace"] = "processlayer"
        helper.validate_sealed(value, "processlayer")
        with self.assertRaises(helper.SafeFailure):
            helper.validate_sealed(value)
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            cert = folder / "public.pem"
            cert.write_text("-----BEGIN CERTIFICATE-----\nfixture-public-only\n")
            original = folder / helper.SEALED_FILE
            original.write_text("preserve-production-ciphertext")
            def command(args, payload=None):
                if args[0] == "openssl":
                    return b""
                self.assertEqual(json.loads(payload)["metadata"], {"name": helper.NAME, "namespace": "processlayer"})
                self.assertIn("strict", args)
                return json.dumps(value).encode()
            auth = base64.b64encode((helper.OWNER + ":" + DUMMY).encode()).decode()
            with patch.object(helper, "command", side_effect=command), patch.object(helper, "read_token", return_value=DUMMY), patch.object(helper, "verify_access", return_value=auth):
                output = helper.prepare(cert, folder, "processlayer")
            self.assertEqual(output.name, "staging-" + helper.SEALED_FILE)
            self.assertEqual(original.read_text(), "preserve-production-ciphertext")
            helper.validate_sealed(json.loads(output.read_text()), "processlayer")
            self.assertNotIn(DUMMY, output.read_text())

    def test_existing_output_and_symlink_refused_before_token_prompt(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            cert = folder / "public.pem"
            cert.write_text("fixture-public-only")
            output = folder / helper.SEALED_FILE
            output.write_text("preserve-this-ciphertext")
            with patch.object(helper, "read_token") as prompt:
                with self.assertRaises(helper.SafeFailure):
                    helper.prepare(cert, folder)
                prompt.assert_not_called()
            self.assertEqual(output.read_text(), "preserve-this-ciphertext")
            output.unlink()
            try:
                output.symlink_to(folder / "absent")
            except OSError:
                self.skipTest("Host does not permit local symlinks")
            with patch.object(helper, "read_token") as prompt:
                with self.assertRaises(helper.SafeFailure):
                    helper.prepare(cert, folder)
                prompt.assert_not_called()
            self.assertTrue(output.is_symlink())

    def test_failure_and_interrupt_remove_reserved_output_without_logging_details(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            cert = folder / "public.pem"
            cert.write_text("-----BEGIN CERTIFICATE-----\nfixture-public-only\n")
            for failure in (helper.SafeFailure("Verification failed"), KeyboardInterrupt()):
                with patch.object(helper, "command", return_value=b""), patch.object(helper, "read_token", side_effect=failure):
                    with self.assertRaises(type(failure)):
                        helper.prepare(cert, folder)
                self.assertFalse((folder / helper.SEALED_FILE).exists())


class WiringTests(unittest.TestCase):
    def test_flux_active_with_ciphertext_and_synced_readiness_gate(self):
        resource = yaml.safe_load((ROOT / "clusters/production/processlayer-registry-credentials.yaml").read_text())
        self.assertEqual(resource["metadata"], {"name": "processlayer-registry-credentials", "namespace": "flux-system"})
        self.assertIs(resource["spec"]["prune"], False)
        self.assertIs(resource["spec"]["wait"], True)
        self.assertEqual(resource["spec"]["path"], "./platform/app-bootstrap/processlayer-registry")
        self.assertEqual(resource["spec"]["sourceRef"], {"kind": "GitRepository", "name": "flux-system"})
        self.assertIn("'Synced'", resource["spec"]["healthCheckExprs"][0]["current"])
        self.assertIn("'True'", resource["spec"]["healthCheckExprs"][0]["current"])
        root = yaml.safe_load((ROOT / "clusters/production/kustomization.yaml").read_text())
        self.assertIn("processlayer-registry-credentials.yaml", root["resources"])
        helper.validate_sealed(json.loads(Path(__file__).with_name(helper.SEALED_FILE).read_text()))
        helper.validate_sealed(json.loads(Path(__file__).with_name("staging-" + helper.SEALED_FILE).read_text()), "processlayer")
        apps = yaml.safe_load((ROOT / "clusters/production/processlayer-applications.yaml").read_text())
        self.assertIn({"name": "processlayer-registry-credentials"}, apps["spec"]["dependsOn"])
        production = yaml.safe_load((ROOT / "platform/app-bootstrap/processlayer-applications/production.yaml").read_text())
        self.assertEqual(production["metadata"]["annotations"]["processlayer.ai/registry-prerequisite"], "processlayer-registry-pull-2026-11-04")

    def test_render_fixture_stays_outside_repository(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            (folder / "kustomization.yaml").write_text(Path(__file__).with_name("kustomization.yaml").read_text())
            (folder / helper.SEALED_FILE).write_text(json.dumps(sealed_fixture()))
            staging = sealed_fixture()
            staging["metadata"]["namespace"] = "processlayer"
            staging["spec"]["template"]["metadata"]["namespace"] = "processlayer"
            (folder / ("staging-" + helper.SEALED_FILE)).write_text(json.dumps(staging))
            rendered = subprocess.check_output(["kubectl", "kustomize", str(folder)], text=True)
            resources = list(yaml.safe_load_all(rendered))
            self.assertEqual(len(resources), 2)
            self.assertEqual({r["metadata"]["namespace"] for r in resources}, {"processlayer", "processlayer-prod"})
            for resource in resources:
                helper.validate_sealed(resource, resource["metadata"]["namespace"])
            self.assertNotIn(DUMMY, rendered)


if __name__ == "__main__":
    unittest.main()
