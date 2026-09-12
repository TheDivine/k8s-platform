#!/usr/bin/env python3
"""Verify private image access, then write only a strictly scoped SealedSecret."""
import base64
import getpass
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request
import warnings

DIGEST = '28cf582461140c699520dd4b83eebdaea8afe377119da54521e9cdb53f95d875'
OUTPUT = 'landing-page-ghcr-read.updated.sealed.json'


class SafeFailure(Exception):
    """Failure text that is safe to show without credential or response details."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def read_token():
    """Read from the controlling terminal without echo; never fall back to echoed stdin."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            return getpass.getpass('TheDivine classic PAT, read:packages (hidden): ').strip()
    except (getpass.GetPassWarning, EOFError, OSError, io.UnsupportedOperation):
        raise SafeFailure('Could not open a hidden interactive token prompt on this terminal.') from None


def prepare(token, fetch, seal):
    auth = base64.b64encode(('TheDivine:' + token).encode()).decode()
    try:
        session = json.loads(fetch(
            'https://ghcr.io/token?service=ghcr.io&scope=repository%3Athedivine%2Flanding-page-service%3Apull',
            {'Authorization': 'Basic ' + auth}))
    except urllib.error.HTTPError as error:
        raise SafeFailure(
            f'GHCR rejected the classic PAT at the token request (HTTP {error.code}). '
            'Confirm the token belongs to TheDivine and has read:packages.') from None
    except (urllib.error.URLError, OSError):
        raise SafeFailure('Could not reach the GHCR token service. Check DNS and outbound HTTPS.') from None
    except (json.JSONDecodeError, TypeError):
        raise SafeFailure('GHCR token service returned an unexpected response.') from None
    bearer = session.get('token') or session.get('access_token')
    if not bearer:
        raise SafeFailure('GHCR did not issue a registry access token for this package.')
    try:
        manifest = fetch(
            'https://ghcr.io/v2/thedivine/landing-page-service/manifests/sha256:' + DIGEST,
            {'Authorization': 'Bearer ' + bearer,
             'Accept': 'application/vnd.oci.image.index.v1+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.docker.distribution.manifest.v2+json'})
    except urllib.error.HTTPError as error:
        raise SafeFailure(
            f'GHCR issued a token but denied the private image manifest (HTTP {error.code}). '
            'Confirm TheDivine has package access and the PAT has read:packages.') from None
    except (urllib.error.URLError, OSError):
        raise SafeFailure('Could not reach the GHCR image service. Check DNS and outbound HTTPS.') from None
    if hashlib.sha256(manifest).hexdigest() != DIGEST:
        raise SafeFailure('GHCR returned a manifest that did not match the pinned production digest.')
    metadata = {'name': 'landing-page-ghcr-read', 'namespace': 'landing-page-service'}
    config = json.dumps({'auths': {'ghcr.io': {'auth': auth}}})
    secret = {'apiVersion': 'v1', 'kind': 'Secret', 'metadata': metadata,
              'type': 'kubernetes.io/dockerconfigjson', 'data': {
                  '.dockerconfigjson': base64.b64encode(config.encode()).decode()}}
    try:
        encrypted = json.loads(seal(json.dumps(secret)))
    except (json.JSONDecodeError, TypeError):
        raise SafeFailure('kubeseal returned output that was not valid JSON.') from None
    if (encrypted.get('kind') != 'SealedSecret' or encrypted.get('data') or
            encrypted.get('stringData') or encrypted['spec'].get('template', {}).get('data') or
            encrypted['spec'].get('encryptedData', {}).get('.dockerconfigjson', '') == ''):
        raise SafeFailure('kubeseal output did not contain the expected encrypted field.')
    for key, value in metadata.items():
        if encrypted['metadata'].get(key) != value:
            raise SafeFailure('kubeseal output targeted an unexpected name or namespace.')
    return json.dumps(encrypted, indent=2) + '\n'


def main():
    if Path(OUTPUT).exists():
        raise SafeFailure(f'{OUTPUT} already exists. Preserve it, then run from a clean folder.')
    opener = urllib.request.build_opener(NoRedirect())

    def fetch(url, headers):
        with opener.open(urllib.request.Request(url, headers=headers), timeout=30) as response:
            data = response.read(1024 * 1024 + 1)
            if len(data) > 1024 * 1024:
                raise SafeFailure('GHCR response exceeded the expected size limit.')
            return data

    def seal(payload):
        try:
            result = subprocess.run([
                'kubeseal', '--controller-name=sealed-secrets-controller',
                '--controller-namespace=sealed-secrets', '--scope=strict', '--format=json'],
                input=payload, capture_output=True, text=True, timeout=60)
        except FileNotFoundError:
            raise SafeFailure('kubeseal is not installed or is not available on PATH.') from None
        except subprocess.TimeoutExpired:
            raise SafeFailure('kubeseal timed out while contacting the Sealed Secrets controller.') from None
        if result.returncode:
            raise SafeFailure(
                'kubeseal could not contact sealed-secrets/sealed-secrets-controller or seal the Secret. '
                'Verify the current kubectl context and controller name.')
        return result.stdout

    token = read_token()
    if not token:
        raise SafeFailure('No token was entered.')
    encrypted = prepare(token, fetch, seal)
    with open(OUTPUT, 'x') as output:
        output.write(encrypted)
    print('Exact image access verified. Encrypted output: ' + OUTPUT)
    print('No cluster resources changed. Share only this encrypted file for the GitOps update.')


if __name__ == '__main__':
    try:
        main()
    except SafeFailure as error:
        print(f'Stopped: {error}', file=sys.stderr)
        print('No cluster changes made.', file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        # Print only the exception class, never provider bodies, subprocess output or credentials.
        print(f'Stopped: unexpected local failure ({type(error).__name__}).', file=sys.stderr)
        print('No cluster changes made.', file=sys.stderr)
        sys.exit(1)
