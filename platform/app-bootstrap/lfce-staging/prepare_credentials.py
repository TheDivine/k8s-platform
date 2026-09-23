#!/usr/bin/env python3
"""Prepare strictly scoped SealedSecrets on the admin server; never apply them."""
import argparse
import base64
import getpass
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

NAMESPACE = 'lfce-staging'
IMAGES = {
    'thedivine/lfce-backend': 'sha256:7f8b44fe126645938bc4ed54888bf77d248cd354df4660a3e9eca0af44b235b0',
    'thedivine/lfce-frontend': 'sha256:1bddf5ed8a9525c2b16b62ef703eac4dfce0d76f0703aee89c9cc357362db763',
}
APP_KEYS = {'DATABASE_URL', 'POSTGRES_PASSWORD', 'DASHBOARD_ADMIN_EMAIL',
            'DASHBOARD_AUTH_KEY', 'INTEGRATION_AUTH_KEY'}


def command(args, data=None):
    result = subprocess.run(args, input=data, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=45)
    if result.returncode:
        raise RuntimeError(args[0] + ' failed; inspect tool access privately')
    return result.stdout


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Unexpected registry redirect')


def verify_registry(auth):
    """Verify both exact image indexes with the credential that will be sealed."""
    opener = urllib.request.build_opener(NoRedirect)
    for package, digest in IMAGES.items():
        query = urllib.parse.urlencode({'service': 'ghcr.io', 'scope': f'repository:{package}:pull'})
        request = urllib.request.Request('https://ghcr.io/token?' + query,
                                         headers={'Authorization': 'Basic ' + auth})
        with opener.open(request, timeout=20) as response:
            token = json.load(response)['token']
        request = urllib.request.Request(f'https://ghcr.io/v2/{package}/manifests/{digest}',
            headers={'Authorization': 'Bearer ' + token,
                     'Accept': 'application/vnd.oci.image.index.v1+json'})
        with opener.open(request, timeout=20) as response:
            index = json.load(response)
            if response.headers.get('Docker-Content-Digest') != digest:
                raise ValueError('Registry digest mismatch')
        platforms = {(item.get('platform', {}).get('os'), item.get('platform', {}).get('architecture'))
                     for item in index.get('manifests', [])}
        if not {('linux', 'amd64'), ('linux', 'arm64')} <= platforms:
            raise ValueError('Required image platforms missing')


def secret(name, values, kind='Opaque'):
    return {'apiVersion': 'v1', 'kind': 'Secret',
            'metadata': {'name': name, 'namespace': NAMESPACE}, 'type': kind,
            'data': {key: base64.b64encode(value.encode()).decode() for key, value in values.items()}}


def validated_sealed(obj, name, kind, keys):
    meta = obj.get('metadata', {})
    spec = obj.get('spec', {})
    template = spec.get('template', {})
    for metadata in (meta, template.get('metadata', {})):
        if metadata.get('name') != name or metadata.get('namespace') != NAMESPACE:
            raise ValueError('SealedSecret scope mismatch')
        annotations = metadata.get('annotations', {})
        if any(key in annotations for key in ('sealedsecrets.bitnami.com/cluster-wide',
                                              'sealedsecrets.bitnami.com/namespace-wide')):
            raise ValueError('Broad secret scope rejected')
    encrypted = spec.get('encryptedData', {})
    if (obj.get('apiVersion') != 'bitnami.com/v1alpha1' or obj.get('kind') != 'SealedSecret'
            or template.get('type') != kind or template.get('data') or template.get('stringData')
            or set(encrypted) != set(keys)):
        raise ValueError('Invalid encrypted secret shape')
    for value in encrypted.values():
        if len(base64.b64decode(value, validate=True)) < 64:
            raise ValueError('Invalid ciphertext')
    # Export only encrypted data and explicit scope, never arbitrary tool fields.
    return {'apiVersion': 'bitnami.com/v1alpha1', 'kind': 'SealedSecret',
            'metadata': {'name': name, 'namespace': NAMESPACE},
            'spec': {'encryptedData': encrypted, 'template': {
                'metadata': {'name': name, 'namespace': NAMESPACE}, 'type': kind}}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', required=True, help='Exact kubectl context; never implicitly uses current context')
    parser.add_argument('--output', default='lfce-bootstrap-private', help='New private directory; existing paths are refused')
    parser.add_argument('--registry-source', help='Optional existing namespace/secret with GHCR pull access')
    args = parser.parse_args()
    if not sys.stdin.isatty():
        raise ValueError('Run interactively on the admin server for hidden credential entry')
    os.umask(0o077)
    destination = Path(args.output).resolve()
    if destination.exists():
        raise ValueError('Output directory exists; keep the previous credentials, do not regenerate')
    kube = ['kubectl', '--context', args.context, '--request-timeout=15s']
    print('Checking cluster access, existing LFCE resources, Longhorn and issuer...')
    command(kube + ['get', '--raw=/readyz'])
    for name in ('lfce-staging-secrets', 'ghcr-pull'):
        existing = command(kube + ['-n', NAMESPACE, 'get', 'secret', name, '--ignore-not-found', '-o', 'name'])
        if existing.strip():
            raise ValueError('Target secret already exists; credential rotation is a separate operation')
    existing_pvc = command(kube + ['-n', NAMESPACE, 'get', 'pvc', '-o', 'json'])
    if json.loads(existing_pvc).get('items'):
        raise ValueError('Existing data volumes require a migration review before first bootstrap')
    command(kube + ['get', 'storageclass', 'longhorn', '-o', 'name'])
    issuer = json.loads(command(kube + ['get', 'clusterissuer', 'letsencrypt-production-cloudflare', '-o', 'json']))
    if not any(c.get('type') == 'Ready' and c.get('status') == 'True'
               for c in issuer.get('status', {}).get('conditions', [])):
        raise ValueError('Certificate issuer is not Ready')
    nodes = json.loads(command(kube + ['get', 'nodes', '-o', 'json']))
    if not any(any(c.get('type') == 'Ready' and c.get('status') == 'True'
                   for c in node.get('status', {}).get('conditions', [])) for node in nodes.get('items', [])):
        raise ValueError('No Ready nodes')
    seal = ['kubeseal', '--context', args.context, '--controller-name', 'sealed-secrets-controller',
            '--controller-namespace', 'sealed-secrets']
    certificate = command(seal + ['--fetch-cert'])
    print('Cluster prerequisites passed; checking registry access next...')
    if args.registry_source:
        namespace, name = args.registry_source.split('/')
        source = json.loads(command(kube + ['-n', namespace, 'get', 'secret', name, '-o', 'json']))
        if source.get('type') != 'kubernetes.io/dockerconfigjson':
            raise ValueError('Expected a dockerconfigjson source')
        config = json.loads(base64.b64decode(source['data']['.dockerconfigjson'], validate=True))
        entry = config.get('auths', {}).get('ghcr.io', {})
        auth = entry.get('auth')
        if not auth and entry.get('username') and entry.get('password'):
            auth = base64.b64encode((entry['username'] + ':' + entry['password']).encode()).decode()
        if not auth:
            raise ValueError('No GHCR credential in source')
    else:
        username = input('GitHub username with access to both LFCE packages: ').strip()
        token = getpass.getpass('GHCR read:packages token (hidden): ')
        auth = base64.b64encode((username + ':' + token).encode()).decode()
    verify_registry(auth)
    print('Both LFCE image digests and required platforms are accessible.')
    email = input('LFCE dashboard administrator email: ').strip()
    if '@' not in email or any(char.isspace() for char in email):
        raise ValueError('Invalid email')
    password = secrets.token_hex(32)
    values = {'POSTGRES_PASSWORD': password,
              'DATABASE_URL': f'postgres://lfce:{password}@lfce-postgres:5432/lfce',
              'DASHBOARD_ADMIN_EMAIL': email, 'DASHBOARD_AUTH_KEY': secrets.token_urlsafe(36),
              'INTEGRATION_AUTH_KEY': secrets.token_urlsafe(36)}
    materials = [secret('lfce-staging-secrets', values), secret('ghcr-pull', {
        '.dockerconfigjson': json.dumps({'auths': {'ghcr.io': {'auth': auth}}})}, 'kubernetes.io/dockerconfigjson')]
    encrypted = []
    with tempfile.TemporaryDirectory(prefix='lfce-public-cert-') as temp:
        cert_path = Path(temp) / 'controller.pem'
        cert_path.write_bytes(certificate)
        for item in materials:
            output = json.loads(command(['kubeseal', '--cert', str(cert_path), '--scope', 'strict', '--format', 'json'],
                                        json.dumps(item).encode()))
            encrypted.append(validated_sealed(output, item['metadata']['name'], item['type'], item['data']))
    destination.mkdir(mode=0o700)
    (destination / 'operator-credentials.PRIVATE.json').write_text(json.dumps(values, indent=2) + '\n')
    (destination / 'lfce-bootstrap.sealed.json').write_text(json.dumps({
        'apiVersion': 'v1', 'kind': 'List', 'items': encrypted}, indent=2) + '\n')
    print('Prepared: ' + str(destination))
    print('Return ONLY lfce-bootstrap.sealed.json. Keep operator-credentials.PRIVATE.json private and backed up.')
    print('Verified both image digests, Longhorn, Ready issuer, Ready node and sealing certificate. No resources applied.')


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        # Remote stderr and exception messages can include credentials.
        print('Stopped (' + type(error).__name__ + '). No cluster resources were changed. Check prerequisites privately.')
        raise SystemExit(1)
