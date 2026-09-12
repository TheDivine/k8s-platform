#!/usr/bin/env python3
"""Verify private image access, then write only a strictly scoped SealedSecret."""
import base64
import getpass
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

DIGEST = '28cf582461140c699520dd4b83eebdaea8afe377119da54521e9cdb53f95d875'
OUTPUT = 'landing-page-ghcr-read.updated.sealed.json'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def prepare(token, fetch, seal):
    auth = base64.b64encode(('TheDivine:' + token).encode()).decode()
    session = json.loads(fetch(
        'https://ghcr.io/token?service=ghcr.io&scope=repository%3Athedivine%2Flanding-page-service%3Apull',
        {'Authorization': 'Basic ' + auth}))
    bearer = session.get('token') or session.get('access_token')
    if not bearer:
        raise ValueError('No registry access token')
    manifest = fetch(
        'https://ghcr.io/v2/thedivine/landing-page-service/manifests/sha256:' + DIGEST,
        {'Authorization': 'Bearer ' + bearer,
         'Accept': 'application/vnd.oci.image.index.v1+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.docker.distribution.manifest.v2+json'})
    if hashlib.sha256(manifest).hexdigest() != DIGEST:
        raise ValueError('Pinned image manifest did not match')
    metadata = {'name': 'landing-page-ghcr-read', 'namespace': 'landing-page-service'}
    config = json.dumps({'auths': {'ghcr.io': {'auth': auth}}})
    secret = {'apiVersion': 'v1', 'kind': 'Secret', 'metadata': metadata,
              'type': 'kubernetes.io/dockerconfigjson', 'data': {
                  '.dockerconfigjson': base64.b64encode(config.encode()).decode()}}
    encrypted = json.loads(seal(json.dumps(secret)))
    if (encrypted.get('kind') != 'SealedSecret' or encrypted.get('data') or
            encrypted.get('stringData') or encrypted['spec'].get('template', {}).get('data') or
            encrypted['spec'].get('encryptedData', {}).get('.dockerconfigjson', '') == ''):
        raise ValueError('Expected encrypted SealedSecret output')
    for key, value in metadata.items():
        if encrypted['metadata'].get(key) != value:
            raise ValueError('Unexpected SealedSecret target')
    return json.dumps(encrypted, indent=2) + '\n'


def main():
    if Path(OUTPUT).exists():
        raise ValueError('Output already exists; preserve it and choose a clean folder')
    opener = urllib.request.build_opener(NoRedirect())

    def fetch(url, headers):
        with opener.open(urllib.request.Request(url, headers=headers), timeout=30) as response:
            data = response.read(1024 * 1024 + 1)
            if len(data) > 1024 * 1024:
                raise ValueError('Unexpected response size')
            return data

    def seal(payload):
        result = subprocess.run([
            'kubeseal', '--controller-name=sealed-secrets-controller',
            '--controller-namespace=sealed-secrets', '--scope=strict', '--format=json'],
            input=payload, capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise ValueError('Sealing failed')
        return result.stdout

    # Explicit TTY: fail closed rather than falling back to echoed stdin.
    with open('/dev/tty', 'r+') as terminal:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            token = getpass.getpass('TheDivine classic PAT, read:packages (hidden): ', stream=terminal).strip()
    if not token:
        raise ValueError('Empty token')
    encrypted = prepare(token, fetch, seal)
    with open(OUTPUT, 'x') as output:
        output.write(encrypted)
    print('Exact image access verified. Encrypted output: ' + OUTPUT)
    print('No cluster resources changed. Share only this encrypted file for the GitOps update.')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        # Never print provider response bodies, subprocess stderr or credential values.
        print('Stopped: image authorization, sealing or output check failed. No cluster changes made.', file=sys.stderr)
        sys.exit(1)
