import unittest
from unittest.mock import patch, Mock, mock_open
import json
import jwt
from requests.models import Response
from requests.exceptions import HTTPError

from certbot import errors
from certbot_dns_stackit.stackit import _StackitClient, RRSet, Record, Authenticator


class TestStackitClient(unittest.TestCase):
    def setUp(self):
        self.client = _StackitClient("test_token", "test_project", "https://test.url")
        self.mock_response = Mock()
        self.mock_rrset = Mock(
            id="rrset_id_test", records=[Mock(content="existing_validation_test")]
        )

    def test_get_zone_id_success(self):
        self.mock_response.json.return_value = {"zones": [{"id": "12345"}]}
        self.mock_response.status_code = 200

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            zone_id = self.client._get_zone_id("test_domain")
            self.assertEqual(zone_id, "12345")
            mock_get.assert_called_once()

    def test_get_zone_id_failure(self):
        self.mock_response.status_code = 404

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            with self.assertRaises(errors.PluginError):
                self.client._get_zone_id("test_domain")
            mock_get.assert_called_once()

    def test_create_rrset(self):
        self.mock_response.status_code = 202

        with patch("requests.post", return_value=self.mock_response) as mock_post:
            self.client._create_rrset(
                "zone_123", "validation_name_test", "validation_test"
            )
            mock_post.assert_called_once()

    def test_create_rrset_failure(self):
        self.mock_response.status_code = 400
        self.mock_response.text = "Bad Request"

        with patch.object(self.client, "_get_zone_id", return_value="zone_123"):
            with patch("requests.post", return_value=self.mock_response):
                with self.assertRaises(errors.PluginError) as context:
                    self.client._create_rrset(
                        "zone_123", "validation_name_test", "validation_test"
                    )

                self.assertEqual(
                    str(context.exception),
                    "Could not create rrset for zone id zone_123. Response: Bad Request",
                )

    def test_add_record_to_rrset(self):
        self.mock_response.status_code = 202

        with patch("requests.patch", return_value=self.mock_response) as mock_patch:
            self.client._add_record_to_rrset(
                "zone_123", "rrset_id_test", "validation_test"
            )
            mock_patch.assert_called_once()

    def test_add_record_to_rrset_failure(self):
        self.mock_response.status_code = 400
        self.mock_response.text = "Bad Request"

        with patch("requests.patch", return_value=self.mock_response):
            with self.assertRaises(errors.PluginError) as context:
                self.client._add_record_to_rrset(
                    "zone_123", "rrset_id_test", "validation_test"
                )

            self.assertEqual(
                str(context.exception),
                "Could not add record to rrset rrset_id_test. Response: Bad Request",
            )

    def test_get_rrset_exists(self):
        self.mock_response.json.return_value = {
            "rrSets": [
                {
                    "id": "rrset_id_test",
                    "records": [{"content": "test_content", "id": "record_id_test"}],
                }
            ]
        }
        self.mock_response.status_code = 200

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            rrset = self.client._get_rrset("zone_123", "validation_name_test")
            self.assertIsInstance(rrset, RRSet)
            self.assertEqual(rrset.id, "rrset_id_test")
            self.assertIsInstance(rrset.records[0], Record)
            mock_get.assert_called_once()

    def test_get_rrset_not_exists(self):
        self.mock_response.json.return_value = {"rrSets": []}
        self.mock_response.status_code = 200

        with patch("requests.get", return_value=self.mock_response) as mock_get:
            rrset = self.client._get_rrset("zone_123", "validation_name_test")
            self.assertIsNone(rrset)
            mock_get.assert_called_once()

    def test_get_rrset_failure(self):
        self.mock_response.status_code = 400
        self.mock_response.text = "Bad Request"

        with patch("requests.get", return_value=self.mock_response):
            with self.assertRaises(errors.PluginError) as context:
                self.client._get_rrset("zone_123", "validation_name_test")

            expected_msg = "Could not find rrset id for zone id zone_123 and validation name validation_name_test., Response: Bad Request"
            self.assertEqual(str(context.exception), expected_msg)

    def test_del_txt_record(self):
        self.mock_response.status_code = 202
        with patch.object(
            self.client, "_get_zone_id", return_value="zone_123"
        ) as mock_get_zone_id, patch.object(
            self.client,
            "_get_rrset",
            return_value=RRSet(id="rrset_id_test", records=[]),
        ) as mock_get_rrset, patch(
            "requests.delete", return_value=self.mock_response
        ) as mock_delete:
            self.client.del_txt_record(
                "test_domain", "validation_name_test", "validation_test"
            )
            mock_get_zone_id.assert_called_once()
            mock_get_rrset.assert_called_once()
            mock_delete.assert_called_once()

    def test_delete_record_set(self):
        self.mock_response.status_code = 202

        with patch("requests.delete", return_value=self.mock_response) as mock_delete:
            self.client._delete_record_set("zone_123", "rrset_id_test")
            mock_delete.assert_called_once()

    def test_delete_record_set_failure(self):
        self.mock_response.status_code = 400
        self.mock_response.text = "Bad Request"

        with patch("requests.delete", return_value=self.mock_response):
            with self.assertRaises(errors.PluginError) as context:
                self.client._delete_record_set("zone_123", "rrset_id_test")

            self.assertEqual(
                str(context.exception),
                "Could not delete rrset id rrset_id_test. Response: Bad Request",
            )

    def test_add_txt_record_no_rrset(self):
        with patch.object(
            self.client, "_get_zone_id", return_value="zone_123"
        ) as mock_get_zone_id, patch.object(
            self.client, "_get_rrset", return_value=None
        ) as mock_get_rrset, patch.object(
            self.client, "_create_rrset"
        ) as mock_create_rrset:
            self.client.add_txt_record(
                "test_domain", "validation_name_test", "validation_test"
            )

            mock_get_zone_id.assert_called_once()
            mock_get_rrset.assert_called_once()
            mock_create_rrset.assert_called_once_with(
                "zone_123", "validation_name_test", "validation_test"
            )

    def test_add_txt_record_with_rrset_without_validation(self):
        with patch.object(
            self.client, "_get_zone_id", return_value="zone_123"
        ) as mock_get_zone_id, patch.object(
            self.client, "_get_rrset", return_value=self.mock_rrset
        ) as mock_get_rrset, patch.object(
            self.client, "_add_record_to_rrset"
        ) as mock_add_record:
            self.client.add_txt_record(
                "test_domain", "validation_name_test", "new_validation_test"
            )

            mock_get_zone_id.assert_called_once()
            mock_get_rrset.assert_called_once()
            mock_add_record.assert_called_once_with(
                "zone_123", "rrset_id_test", "new_validation_test"
            )

    def test_add_txt_record_with_rrset_with_validation(self):
        with patch.object(
            self.client, "_get_zone_id", return_value="zone_123"
        ) as mock_get_zone_id, patch.object(
            self.client, "_get_rrset", return_value=self.mock_rrset
        ) as mock_get_rrset:
            self.client.add_txt_record(
                "test_domain", "validation_name_test", "existing_validation_test"
            )

            mock_get_zone_id.assert_called_once()
            mock_get_rrset.assert_called_once()
            # Assert that _add_record_to_rrset wasn't called because validation already exists in rrset
            with self.assertRaises(AttributeError):
                self.client._add_record_to_rrset.assert_called_once()


class TestAuthenticator(unittest.TestCase):
    def setUp(self):
        mock_config = Mock()
        mock_name = Mock()
        self.authenticator = Authenticator(mock_config, mock_name)

    @patch.object(Authenticator, "conf")
    @patch.object(Authenticator, "_configure_credentials")
    def test_setup_credentials_with_service_account(self, mock_configure_credentials, mock_conf):
        # Simulate `service_account` being set
        mock_conf.return_value = 'service_account_value'

        self.authenticator._setup_credentials()

        # Assert _configure_credentials was not called
        mock_configure_credentials.assert_not_called()
        # Assert service_account is set correctly
        self.assertEqual(self.authenticator.service_account, 'service_account_value')

    @patch.object(Authenticator, "conf")
    @patch.object(Authenticator, "_configure_credentials")
    def test_setup_credentials_without_service_account(self, mock_configure_credentials, mock_conf):
        # Simulate `service_account` not being set
        mock_conf.return_value = None
        mock_creds = Mock()
        mock_configure_credentials.return_value = mock_creds

        self.authenticator._setup_credentials()

        # Assert _configure_credentials was called with the correct arguments
        mock_configure_credentials.assert_called_once_with(
            "credentials",
            "STACKIT credentials for the STACKIT DNS API",
            {
                "project_id": "Specifies the project id of the STACKIT project.",
                "auth_token": "Defines the authentication token for the STACKIT DNS API. Keep in mind that the "
                "service account to this token need to have project edit permissions as we create txt "
                "records in the zone",
            },
        )
        # Assert credentials are set correctly
        self.assertEqual(self.authenticator.credentials, mock_creds)

    @patch.object(Authenticator, "_get_stackit_client")
    def test_perform(self, mock_get_client):
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        self.authenticator._perform(
            "test_domain", "validation_name_test", "validation_test"
        )

        mock_get_client.assert_called_once()
        mock_client.add_txt_record.assert_called_once_with(
            "test_domain", "validation_name_test", "validation_test"
        )

    @patch.object(Authenticator, "_get_stackit_client")
    def test_cleanup(self, mock_get_client):
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        self.authenticator._cleanup(
            "test_domain", "validation_name_test", "validation_test"
        )

        mock_get_client.assert_called_once()
        mock_client.del_txt_record.assert_called_once_with(
            "test_domain", "validation_name_test", "validation_test"
        )

    @patch("builtins.open", new_callable=mock_open, read_data='{"credentials": {"iss": "test_iss", "sub": "test_sub", "aud": "test_aud", "kid": "test_kid", "privateKey": "test_private_key"}}')
    @patch("json.load", lambda x: json.loads(x.read()))
    def test_load_service_file(self, mock_load_service_file):
        expected_credentials = {
            "iss": "test_iss",
            "sub": "test_sub",
            "aud": "test_aud",
            "kid": "test_kid",
            "privateKey": "test_private_key",
        }

        credentials = self.authenticator._load_service_file("dummy_path")
        self.assertEqual(credentials, expected_credentials)

    @patch("builtins.open", side_effect=FileNotFoundError())
    @patch("logging.error")
    def test_load_service_file_not_found(self, mock_log, mock_file):
        result = self.authenticator._load_service_file("nonexistent_path")
        self.assertIsNone(result)
        mock_log.assert_called()

    @patch("jwt.encode")
    def test_generate_jwt(self, mock_jwt_encode):
        credentials = {
            'iss': 'issuer',
            'sub': 'subject',
            'aud': 'audience',
            'kid': 'key_id',
            'privateKey': 'private_key'
        }
        self.authenticator._generate_jwt(credentials)
        mock_jwt_encode.assert_called()

    def test_generate_jwt_fail(self):
        credentials = {
            'iss': 'issuer',
            'sub': 'subject',
            'aud': 'audience',
            'kid': 'key_id',
            'privateKey': 'not_a_valid_key'
        }
        with self.assertRaises(jwt.exceptions.InvalidKeyError):
            token = self.authenticator._generate_jwt(credentials)
            self.assertIsNone(token)

    @patch('requests.post')
    def test_request_access_token_success(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.raise_for_status = lambda: None  # Mock raise_for_status to do nothing
        mock_response.json.return_value = {'access_token': 'mocked_access_token'}

        result = self.authenticator._request_access_token('jwt_token_example')

        # Assertions
        mock_post.assert_called_once_with(
            'https://service-account.api.stackit.cloud/token',
            data={'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer', 'assertion': 'jwt_token_example'},
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        self.assertEqual(result, 'mocked_access_token')

    @patch('requests.post')
    def test_request_access_token_failure_raises_http_error(self, mock_post):
        mock_response = Response()
        mock_response.status_code = 403
        mock_post.return_value = mock_response
        mock_response.raise_for_status = lambda: (_ for _ in ()).throw(HTTPError())

        with self.assertRaises(errors.PluginError):
            self.authenticator._request_access_token('jwt_token_example')

        mock_post.assert_called_once()

    @patch("builtins.open", new_callable=mock_open, read_data='{"credentials": {"iss": "test_iss", "sub": "test_sub", "aud": "test_aud", "kid": "test_kid", "privateKey": "test_private_key"}}')
    @patch.object(Authenticator, '_request_access_token')
    @patch.object(Authenticator, '_generate_jwt')
    @patch.object(Authenticator, '_load_service_file')
    def test_generate_jwt_token_success(self, mock_load_service_file, mock_generate_jwt, mock_request_access_token, mock_open):
        mock_load_service_file.return_value = {'dummy': 'credentials'}
        mock_generate_jwt.return_value = 'jwt_token_example'
        mock_request_access_token.return_value = 'access_token_example'

        result = self.authenticator._generate_jwt_token('path/to/service/file')

        self.assertEqual(result, 'access_token_example')
        mock_load_service_file.assert_called_once_with('path/to/service/file')
        mock_generate_jwt.assert_called_once_with({'dummy': 'credentials'})
        mock_request_access_token.assert_called_once_with('jwt_token_example')


if __name__ == "__main__":
    unittest.main()
