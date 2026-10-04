"""Offline checks for LFCE's exact health routes and catch-all precedence."""
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parent
HOST = 'lfce-app.xn--cyberlnx-ykb.com'


def matches(path, requested):
    if path['pathType'] == 'Exact':
        return requested == path['path']
    prefix = path['path'].rstrip('/')
    return requested == prefix or requested.startswith(prefix + '/')


def priority(ingress, path):
    explicit = int(ingress['metadata'].get('annotations', {}).get(
        'traefik.ingress.kubernetes.io/router.priority', '0'))
    if explicit:
        return explicit
    # Traefik's standard Ingress provider defaults to generated rule length.
    matcher = 'Path' if path['pathType'] == 'Exact' else 'PathPrefix'
    return len(f"Host(`{HOST}`) && {matcher}(`{path['path']}`)")


class IngressRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = yaml.safe_load((ROOT / 'kustomization.yaml').read_text())
        objects = []
        for resource in config['resources']:
            objects.extend(obj for obj in yaml.safe_load_all(
                (ROOT / resource).read_text()) if obj)
        cls.ingresses = {
            obj['metadata']['name']: obj for obj in objects
            if obj['kind'] == 'Ingress' and any(
                rule.get('host') == HOST for rule in obj['spec']['rules'])
        }
        cls.routes = [
            (ingress, path) for ingress in cls.ingresses.values()
            for rule in ingress['spec']['rules'] if rule.get('host') == HOST
            for path in rule['http']['paths']
        ]

    def test_routes_are_unique_and_preserve_exact_backends(self):
        self.assertEqual(set(self.ingresses), {'lfce', 'lfce-health'})
        observed = [
            (ingress['metadata']['name'], path['path'], path['pathType'],
             path['backend']['service']['name'], path['backend']['service']['port'])
            for ingress, path in self.routes
        ]
        self.assertCountEqual(observed, [
            ('lfce', '/api', 'Prefix', 'lfce-backend', {'name': 'http'}),
            ('lfce', '/', 'Prefix', 'lfce-frontend', {'name': 'http'}),
            ('lfce-health', '/health', 'Exact', 'lfce-backend', {'name': 'http'}),
            ('lfce-health', '/readyz', 'Exact', 'lfce-backend', {'name': 'http'}),
        ])
        self.assertEqual(len({path['path'] for _, path in self.routes}), 4)

    def test_health_priority_beats_every_other_matching_router(self):
        health = self.ingresses['lfce-health']
        self.assertEqual(health['metadata']['annotations'][
            'traefik.ingress.kubernetes.io/router.priority'], '100')
        for requested in ('/health', '/readyz'):
            candidates = [(ingress, path) for ingress, path in self.routes
                          if matches(path, requested)]
            health_paths = [(ingress, path) for ingress, path in candidates
                            if ingress['metadata']['name'] == 'lfce-health']
            self.assertEqual(len(health_paths), 1)
            winner = priority(*health_paths[0])
            alternatives = [(ingress, path) for ingress, path in candidates
                            if ingress['metadata']['name'] != 'lfce-health']
            self.assertTrue(alternatives, 'The frontend catch-all must remain present')
            for ingress, path in alternatives:
                self.assertGreater(winner, priority(ingress, path), requested)
        for requested in ('/health/extra', '/readyz/extra', '/healthcheck'):
            self.assertFalse(any(matches(path, requested) for ingress, path
                                 in self.routes if ingress is health))

    def test_tls_class_and_entrypoint_are_shared(self):
        expected_tls = [{'hosts': [HOST], 'secretName': 'lfce-app-staging-tls'}]
        for ingress in self.ingresses.values():
            self.assertEqual(ingress['metadata']['namespace'], 'lfce-staging')
            self.assertEqual(ingress['spec']['ingressClassName'], 'traefik')
            self.assertEqual(ingress['spec']['tls'], expected_tls)
            annotations = ingress['metadata']['annotations']
            self.assertEqual(annotations[
                'traefik.ingress.kubernetes.io/router.entrypoints'], 'websecure')
            self.assertEqual(annotations[
                'traefik.ingress.kubernetes.io/router.tls'], 'true')


if __name__ == '__main__':
    unittest.main()
