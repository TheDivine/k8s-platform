"""Offline ownership/activation guards; ciphertext fixtures stay outside Git."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml

from test_prepare_repository_key import helper, sealed_fixture


ROOT = Path(__file__).resolve().parents[3]


def read_yaml(path):
    return yaml.safe_load((ROOT / path).read_text())


class GitOpsWiringTests(unittest.TestCase):
    def test_flux_dependency_and_secret_ready_gate(self):
        credentials = read_yaml("clusters/production/processlayer-gitops-credentials.yaml")
        applications = read_yaml("clusters/production/processlayer-applications.yaml")
        for resource in (credentials, applications):
            self.assertEqual(resource["metadata"]["namespace"], "flux-system")
            self.assertIs(resource["spec"]["prune"], False)
            self.assertIs(resource["spec"]["wait"], True)
            self.assertEqual(resource["spec"]["sourceRef"], {"kind": "GitRepository", "name": "flux-system"})
            self.assertNotIn("force", resource["spec"])
        self.assertEqual(applications["spec"]["dependsOn"], [{"name": "processlayer-gitops-credentials"}])
        checks = credentials["spec"]["healthCheckExprs"]
        self.assertEqual(checks[0]["kind"], "SealedSecret")
        self.assertIn("exists", checks[0]["current"])
        self.assertIn("'Synced'", checks[0]["current"])
        self.assertIn("'True'", checks[0]["current"])
        crds = (ROOT / "clusters/production/flux-system/gotk-components.yaml").read_text()
        self.assertIn("healthCheckExprs:", crds)

    def test_same_existing_applications_without_duplicate_registry_owner(self):
        output = subprocess.check_output(["kubectl", "kustomize", str(ROOT / "platform/app-bootstrap/processlayer-applications")], text=True)
        applications = list(yaml.safe_load_all(output))
        # This follow-up includes both existing names after the separately
        # recorded staging/safe-production release gates. Never add duplicates.
        self.assertEqual({item["metadata"]["name"] for item in applications}, {"processlayer", "processlayer-prod"})
        for app in applications:
            self.assertEqual(app["kind"], "Application")
            self.assertEqual(app["metadata"]["namespace"], "argocd")
            self.assertNotIn("finalizers", app["metadata"])
            self.assertEqual(app["spec"]["project"], "default")
            self.assertEqual(app["spec"]["source"]["repoURL"], helper.REPOSITORY)
            self.assertEqual(app["spec"]["source"]["targetRevision"], "main")
            self.assertNotIn("kustomize", app["spec"]["source"])
            production = app["metadata"]["name"] == "processlayer-prod"
            self.assertEqual(app["spec"]["source"]["path"], "infra/k8s/overlays/" + ("production" if production else "staging"))
            self.assertEqual(app["spec"]["destination"]["namespace"], app["metadata"]["name"])
            self.assertEqual(app["spec"]["syncPolicy"]["automated"], {"prune": True, "selfHeal": True})
        for path in (ROOT / "clusters/production/app-registry").glob("*.app.yaml"):
            existing = yaml.safe_load(path.read_text())
            self.assertNotIn(existing["app"]["name"], {"processlayer", "processlayer-prod"})

    def test_credential_render_fixture_is_never_written_into_repository(self):
        with tempfile.TemporaryDirectory(prefix="processlayer-sealed-render-") as temporary:
            directory = Path(temporary)
            shutil.copy(ROOT / "platform/app-bootstrap/processlayer-gitops/kustomization.yaml", directory)
            (directory / helper.SEALED_FILE).write_text(json.dumps(sealed_fixture()))
            rendered = subprocess.check_output(["kubectl", "kustomize", str(directory)], text=True)
            resources = list(yaml.safe_load_all(rendered))
            self.assertEqual(len(resources), 1)
            helper.validate_sealed(resources[0])
            self.assertNotIn("PRIVATE KEY", rendered)

    def test_activation_requires_ciphertext_before_applications(self):
        resources = read_yaml("clusters/production/kustomization.yaml")["resources"]
        credential_file = ROOT / "platform/app-bootstrap/processlayer-gitops" / helper.SEALED_FILE
        if "processlayer-applications.yaml" in resources:
            self.assertIn("processlayer-gitops-credentials.yaml", resources)
        if "processlayer-gitops-credentials.yaml" in resources:
            self.assertTrue(credential_file.is_file(), "Active package needs real ciphertext")
            helper.validate_sealed(json.loads(credential_file.read_text()))
        subprocess.check_output(["kubectl", "kustomize", str(ROOT / "clusters/production")], text=True)


if __name__ == "__main__":
    unittest.main()
