import base64
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('bootstrap',Path(__file__).with_name('prepare_credentials.py'))
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)

class BootstrapTests(unittest.TestCase):
    def test_strict_scope_validation(self):
        for bad in [{}, {'kind':'Secret'}, {'kind':'SealedSecret','metadata':{'name':'relay-auth','namespace':'wrong'}}]:
            with self.assertRaises(ValueError): helper.validate_sealed(bad,'relay-auth')

    def test_mocked_output_contains_no_shared_plaintext(self):
        calls=[]
        raw_config=json.dumps({'auths':{'ghcr.io':{'auth':'test-only'}}}).encode()
        def command(args,data=None):
            calls.append(args)
            if args[0]=='kubectl': return json.dumps({'type':'kubernetes.io/dockerconfigjson','data':{'.dockerconfigjson':base64.b64encode(raw_config).decode()}}).encode()
            if '--fetch-cert' in args: return b'PUBLIC-CERT'
            if args[0]=='kubeseal':
                s=json.loads(data)
                return json.dumps({'kind':'SealedSecret','metadata':s['metadata'],'spec':{'encryptedData':{k:'AgENCRYPTED' for k in s['data']},'template':{'metadata':s['metadata'],'type':s['type']}}}).encode()
            if 'passwd' in args: return b'PASSWORD-HASH'
            if 'genpkey' in args: return b'PRIVATE-KEY'
            return b'-----BEGIN PUBLIC KEY-----\nPUBLICKEY\n-----END PUBLIC KEY-----\n'
        previous=Path.cwd();old_mask=os.umask(0o077)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                os.chdir(tmp);stdout=io.StringIO()
                with patch.object(helper,'command',side_effect=command),patch.object(helper.secrets,'token_urlsafe',return_value='SECRET-PASSWORD'),redirect_stdout(stdout): helper.main()
                folder=next(Path(tmp).glob('processlayer-relay-*'))
                safe=''.join((folder/n).read_text() for n in ('relay-bootstrap.sealed.json','dns-records.json'))+stdout.getvalue()
                for forbidden in ('SECRET-PASSWORD','PRIVATE-KEY','PASSWORD-HASH','test-only'): self.assertNotIn(forbidden,safe)
                self.assertEqual(json.loads((folder/'hestia-settings.PRIVATE.json').read_text())['password'],'SECRET-PASSWORD')
                self.assertTrue(all('apply' not in args for args in calls))
                if os.name!='nt':
                    self.assertEqual(folder.stat().st_mode & 0o777,0o700)
                    for f in folder.iterdir(): self.assertEqual(f.stat().st_mode & 0o777,0o600)
        finally: os.chdir(previous);os.umask(old_mask)

    def test_dependency_failure_writes_nothing(self):
        with patch.object(helper,'command',side_effect=RuntimeError('dependency unavailable')):
            with self.assertRaises(RuntimeError): helper.main()

if __name__=='__main__': unittest.main()
