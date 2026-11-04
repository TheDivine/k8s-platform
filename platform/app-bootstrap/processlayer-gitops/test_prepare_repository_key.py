import base64
from contextlib import redirect_stdout
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("repository_key", Path(__file__).with_name("prepare_repository_key.py"))
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
PRIVATE = b"-----BEGIN OPENSSH PRIVATE KEY-----\nUNIT-TEST-PRIVATE-NOT-A-KEY\n-----END OPENSSH PRIVATE KEY-----\n"
PUBLIC = "ssh-ed25519 " + base64.b64encode(b"synthetic-public-blob").decode() + " unit-test"


def sealed_fixture():
    # Structural test envelope only. Never write this fixture into the Git tree.
    # Include a three-byte plaintext equivalent to catch overly strict overhead
    # assumptions for real kubeseal output (type=git is a short encrypted value).
    encrypted = base64.b64encode(b"\x02\x00" + b"x" * (512 + 16 + 3)).decode()
    return {"apiVersion": "bitnami.com/v1alpha1", "kind": "SealedSecret", "metadata": helper.metadata(),
            "spec": {"encryptedData": {key: encrypted for key in helper.KEYS},
                     "template": {"metadata": helper.metadata(), "type": "Opaque"}}}


class SealedValidationTests(unittest.TestCase):
    def test_expected_strict_scope_and_template_are_accepted(self):
        helper.validate_sealed(sealed_fixture())

    def test_plaintext_wrong_scope_and_missing_labels_fail(self):
        mutations = [
            lambda x: x.update(kind="Secret"),
            lambda x: x.update(data={"private": "value"}),
            lambda x: x["spec"].update(stringData={"private": "value"}),
            lambda x: x["metadata"].update(namespace="wrong"),
            lambda x: x["metadata"].update(name="wrong"),
            lambda x: x["spec"]["template"]["metadata"].update(namespace="wrong"),
            lambda x: x["spec"]["template"]["metadata"].update(labels={}),
            lambda x: x["metadata"].update(annotations={"sealedsecrets.bitnami.com/cluster-wide": "true"}),
            lambda x: x["spec"]["template"]["metadata"].update(annotations={"sealedsecrets.bitnami.com/namespace-wide": "true"}),
            lambda x: x["spec"]["template"].update(data={"private": "value"}),
            lambda x: x["spec"]["encryptedData"].update(sshPrivateKey=base64.b64encode(PRIVATE).decode()),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                candidate = sealed_fixture()
                mutate(candidate)
                with self.assertRaises(ValueError):
                    helper.validate_sealed(candidate)

    def test_command_errors_do_not_disclose_tool_output(self):
        with patch.object(helper.subprocess, "run", return_value=SimpleNamespace(returncode=1, stdout=b"PRIVATE", stderr=b"PRIVATE")):
            with self.assertRaises(RuntimeError) as error:
                helper.command(["kubeseal"])
            self.assertNotIn("PRIVATE", str(error.exception))


@unittest.skipUnless(os.name == "posix", "Run key-file permission tests under Linux/WSL")
class KeyPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="processlayer-key-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cert = self.root / "public.pem"
        self.cert.write_text("-----BEGIN CERTIFICATE-----\nPUBLIC-FIXTURE\n-----END CERTIFICATE-----\n")
        self.output = self.root / "output"
        self.output.mkdir()
        self.calls = []
        self.key_paths = []

    def command(self, args, data=None):
        self.calls.append(args)
        if args[0] == "openssl":
            return b""
        if args[0] == "ssh-keygen":
            path = Path(args[args.index("-f") + 1])
            self.key_paths.append(path)
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
            path.write_bytes(PRIVATE)
            path.with_suffix(".pub").write_text(PUBLIC + "\n")
            return b""
        self.assertEqual(args[0], "kubeseal")
        self.assertEqual(args[args.index("--scope") + 1], "strict")
        self.assertEqual(args[args.index("--cert") + 1], str(self.cert))
        secret = json.loads(data)
        self.assertEqual(secret["metadata"], helper.metadata())
        decoded = {key: base64.b64decode(value) for key, value in secret["data"].items()}
        self.assertEqual(decoded["url"], helper.REPOSITORY.encode())
        self.assertEqual(decoded["project"], b"default")
        self.assertEqual(decoded["sshPrivateKey"], PRIVATE)
        self.assertEqual(stat.S_IMODE(self.key_paths[0].stat().st_mode), 0o600)
        return json.dumps(sealed_fixture()).encode()

    def test_only_encrypted_and_public_outputs_and_private_temp_cleanup(self):
        captured = io.StringIO()
        with patch.object(helper, "command", side_effect=self.command), redirect_stdout(captured):
            files = helper.prepare(self.cert, self.output)
        self.assertEqual({path.name for path in files}, {helper.SEALED_FILE, helper.PUBLIC_FILE})
        self.assertEqual({path.name for path in self.output.iterdir()}, {helper.SEALED_FILE, helper.PUBLIC_FILE})
        safe_output = b"".join(path.read_bytes() for path in files) + captured.getvalue().encode()
        self.assertNotIn(PRIVATE, safe_output)
        self.assertNotIn(base64.b64encode(PRIVATE), safe_output)
        self.assertTrue(all(not path.parent.exists() for path in self.key_paths))
        self.assertTrue(all(stat.S_IMODE(path.stat().st_mode) == 0o600 for path in files))
        self.assertEqual({args[0] for args in self.calls}, {"openssl", "ssh-keygen", "kubeseal"})

    def test_existing_public_or_sealed_file_is_never_overwritten(self):
        for name in (helper.SEALED_FILE, helper.PUBLIC_FILE):
            with self.subTest(name=name):
                existing = self.output / name
                existing.write_text("keep-existing")
                with patch.object(helper, "command") as command:
                    with self.assertRaises(FileExistsError):
                        helper.prepare(self.cert, self.output)
                    command.assert_not_called()
                self.assertEqual(existing.read_text(), "keep-existing")
                existing.unlink()

    def test_sealing_failure_removes_reserved_outputs_and_private_temp(self):
        def fail_sealing(args, data=None):
            if args[0] == "kubeseal":
                raise RuntimeError("simulated sealing failure")
            return self.command(args, data)
        with patch.object(helper, "command", side_effect=fail_sealing):
            with self.assertRaises(RuntimeError):
                helper.prepare(self.cert, self.output)
        self.assertEqual(list(self.output.iterdir()), [])
        self.assertTrue(all(not path.parent.exists() for path in self.key_paths))

    def test_private_key_is_not_accepted_as_certificate_input(self):
        self.cert.write_bytes(PRIVATE)
        with patch.object(helper, "command") as command:
            with self.assertRaises(ValueError):
                helper.prepare(self.cert, self.output)
            command.assert_not_called()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_invalid_sealer_output_fails_closed(self):
        def invalid(args, data=None):
            if args[0] == "kubeseal":
                return json.dumps({"kind": "Secret", "stringData": {"sshPrivateKey": PRIVATE.decode()}}).encode()
            return self.command(args, data)
        with patch.object(helper, "command", side_effect=invalid):
            with self.assertRaises(ValueError):
                helper.prepare(self.cert, self.output)
        self.assertEqual(list(self.output.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
