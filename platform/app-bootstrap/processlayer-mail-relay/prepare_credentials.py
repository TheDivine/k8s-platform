#!/usr/bin/env python3
"""Read existing GHCR secret and seal new relay credentials. Never applies resources.

Run on the admin host with kubectl, kubeseal, openssl and Python 3.8+.
Only relay-bootstrap.sealed.json and dns-records.json are safe to share.
"""
import base64
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile

NAMESPACE = 'processlayer-mail-relay'

def command(args, data=None):
    result = subprocess.run(args, input=data, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=45)
    if result.returncode:
        # Tool stderr may include submitted material; never echo it.
        raise RuntimeError(args[0] + ' failed; no cluster changes made')
    return result.stdout

def secret(name, values, kind='Opaque'):
    return {'apiVersion':'v1','kind':'Secret',
            'metadata':{'name':name,'namespace':NAMESPACE}, 'type':kind,
            'data':{k:base64.b64encode(v).decode() for k,v in values.items()}}

def validate_sealed(value, name):
    if (value.get('kind') != 'SealedSecret' or
        value.get('metadata',{}).get('name') != name or
        value.get('metadata',{}).get('namespace') != NAMESPACE or
        not value.get('spec',{}).get('encryptedData') or
        value.get('spec',{}).get('template',{}).get('data') or
        value.get('spec',{}).get('template',{}).get('stringData') or
        value.get('metadata',{}).get('annotations',{}).get('sealedsecrets.bitnami.com/cluster-wide') or
        value.get('metadata',{}).get('annotations',{}).get('sealedsecrets.bitnami.com/namespace-wide')):
        raise ValueError('Invalid sealed output; stopped')

def main():
    os.umask(0o077)
    # Exact existing source; does not read unrelated cluster credentials.
    existing = json.loads(command(['kubectl','-n','landing-page-service','get','secret',
                                  'landing-page-ghcr-read','-o','json']))
    if existing.get('type') != 'kubernetes.io/dockerconfigjson':
        raise ValueError('Existing GHCR secret has unexpected type')
    dockerconfig = base64.b64decode(existing['data']['.dockerconfigjson'], validate=True)
    if 'ghcr.io' not in json.loads(dockerconfig).get('auths',{}):
        raise ValueError('Existing GHCR secret lacks ghcr.io credentials')
    cert = command(['kubeseal','--controller-name','sealed-secrets-controller',
                    '--controller-namespace','sealed-secrets','--fetch-cert'])
    password = secrets.token_urlsafe(36)
    password_hash = command(['openssl','passwd','-6','-stdin'], password.encode()).strip()
    private_key = command(['openssl','genpkey','-algorithm','RSA','-pkeyopt','rsa_keygen_bits:2048'])
    public_pem = command(['openssl','pkey','-pubout'], private_key).decode()
    public_key = ''.join(x for x in public_pem.splitlines() if not x.startswith('-----'))
    materials = [secret('relay-auth', {'password-hash':password_hash,'dkim-private.pem':private_key}),
                 secret('relay-ghcr-read', {'.dockerconfigjson':dockerconfig}, 'kubernetes.io/dockerconfigjson')]
    with tempfile.TemporaryDirectory(prefix='relay-cert-') as temp:
        cert_path=Path(temp)/'controller.pem'; cert_path.write_bytes(cert)
        sealed=[]
        for item in materials:
            encrypted=json.loads(command(['kubeseal','--cert',str(cert_path),'--scope','strict','--format','json'],json.dumps(item).encode()))
            validate_sealed(encrypted,item['metadata']['name']); sealed.append(encrypted)
    destination=Path(tempfile.mkdtemp(prefix='processlayer-relay-',dir='.')).resolve()
    (destination/'relay-bootstrap.sealed.json').write_text(json.dumps({'apiVersion':'v1','kind':'List','items':sealed},indent=2)+'\n')
    (destination/'dns-records.json').write_text(json.dumps([
        {'type':'A','name':'smtp.processlayerai.com','content':'69.30.233.178','proxied':False},
        {'type':'TXT','name':'relay._domainkey.processlayerai.com','content':'v=DKIM1; k=rsa; p='+public_key}
    ],indent=2)+'\n')
    (destination/'hestia-settings.PRIVATE.json').write_text(json.dumps({
        'domain':'processlayerai.com','host':'smtp.processlayerai.com','port':587,
        'security':'STARTTLS','username':'processlayer-hestia','password':password,
        'note':'Apply only after relay TLS/auth and controlled delivery validation; do not enable Global SMTP.'
    },indent=2)+'\n')
    print('Prepared files in: '+str(destination))
    print('Share ONLY relay-bootstrap.sealed.json and dns-records.json.')
    print('Keep hestia-settings.PRIVATE.json on this server; it contains the password.')
    print('No cluster resources, DNS, Hestia settings or messages changed. Keep these files; do not rerun to rotate credentials unnecessarily.')

if __name__=='__main__':
    try: main()
    except Exception as error:
        print('Stopped: '+type(error).__name__+'. No cluster changes made. Check kubectl/kubeseal/openssl availability and permission to read the existing landing-page secret.')
        raise SystemExit(1)
