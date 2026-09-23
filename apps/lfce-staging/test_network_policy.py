"""Offline assertions for the observed staging ingress namespace contract."""
import unittest
from pathlib import Path

import yaml


class NetworkPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        objects = yaml.safe_load_all(Path(__file__).with_name('resources.yaml').read_text())
        cls.policies = {obj['metadata']['name']: obj['spec'] for obj in objects
                        if obj and obj['kind'] == 'NetworkPolicy'}

    def check_ingress(self, name, namespaces, port):
        policy = self.policies[name]
        self.assertEqual(policy['policyTypes'], ['Ingress'])
        self.assertEqual(len(policy['ingress']), 1)
        rule = policy['ingress'][0]
        expected = [{'namespaceSelector': {'matchLabels': {
            'kubernetes.io/metadata.name': ns}}} for ns in namespaces]
        # Exact peer shapes reject empty peers, wildcard access and stale namespaces.
        self.assertEqual(rule['from'], expected)
        self.assertEqual(rule['ports'], [{'port': port, 'protocol': 'TCP'}])
        self.assertTrue(policy['podSelector']['matchLabels'])

    def test_frontend_allows_only_traefik_namespace(self):
        self.check_ingress('lfce-frontend-ingress', ['traefik'], 3000)

    def test_backend_preserves_internal_access(self):
        self.check_ingress('lfce-backend-ingress', ['traefik', 'lfce-staging'], 3001)

    def test_postgres_stays_internal(self):
        self.check_ingress('lfce-postgres-ingress', ['lfce-staging'], 5432)

    def test_redis_stays_internal(self):
        self.check_ingress('lfce-redis-ingress', ['lfce-staging'], 6379)

    def test_namespace_default_deny_is_preserved(self):
        self.assertEqual(self.policies['lfce-default-deny-ingress'],
                         {'podSelector': {}, 'policyTypes': ['Ingress']})
        self.assertEqual(len(self.policies), 5)


if __name__ == '__main__':
    unittest.main()
