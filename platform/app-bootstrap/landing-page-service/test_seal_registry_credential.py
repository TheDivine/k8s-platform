import base64
import hashlib
import json
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError
import seal_registry_credential as helper


class VerifiedSealingTests(unittest.TestCase):
    def test_rejected_auth_never_seals(self):
        seal = Mock()
        error = HTTPError('https://ghcr.io/token', 403, 'Forbidden', {}, None)
        with self.assertRaisesRegex(helper.SafeFailure, 'token request.*HTTP 403'):
            helper.prepare('fake', Mock(side_effect=error), seal)
        seal.assert_not_called()

    def test_token_without_manifest_access_never_seals(self):
        seal = Mock()
        fetch = Mock(side_effect=[b'{"token":"fake-session"}', OSError()])
        with self.assertRaisesRegex(helper.SafeFailure, 'image manifest.*HTTP 403'):
            error = HTTPError('https://ghcr.io/v2/', 403, 'Forbidden', {}, None)
            fetch = Mock(side_effect=[b'{"token":"fake-session"}', error])
            helper.prepare('fake', fetch, seal)
        seal.assert_not_called()

    def test_wrong_digest_never_seals(self):
        seal = Mock()
        with self.assertRaises(helper.SafeFailure):
            helper.prepare('fake', Mock(side_effect=[b'{"token":"fake-session"}', b'wrong']), seal)
        seal.assert_not_called()

    def test_success_has_correct_target_and_only_encrypted_output(self):
        manifest = b'{"schemaVersion":2}'
        metadata = {'name': 'landing-page-ghcr-read', 'namespace': 'landing-page-service'}
        sealed = {'kind': 'SealedSecret', 'metadata': metadata,
                  'spec': {'encryptedData': {'.dockerconfigjson': 'encrypted-fixture'}}}
        seal = Mock(return_value=json.dumps(sealed))
        with patch.object(helper, 'DIGEST', hashlib.sha256(manifest).hexdigest()):
            result = helper.prepare('fake-credential', Mock(side_effect=[b'{"token":"fake-session"}', manifest]), seal)
        secret = json.loads(seal.call_args.args[0])
        self.assertEqual(secret['metadata'], metadata)
        config = json.loads(base64.b64decode(secret['data']['.dockerconfigjson']))
        self.assertEqual(list(config['auths']), ['ghcr.io'])
        self.assertNotIn('fake-credential', result)
        self.assertEqual(json.loads(result), sealed)

    def test_redirects_are_refused(self):
        self.assertIsNone(helper.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://elsewhere.invalid'))


if __name__ == '__main__':
    unittest.main()
