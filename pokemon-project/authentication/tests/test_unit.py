from django.test import TestCase
from unittest.mock import patch
from rest_framework.response import Response
from ..services import InvalidGoogleIdToken

# Create your tests here.

# Does my view raise an exception if request.data does not have a “credential” key?
# Does my view call GoogleOIDC.verify_token(token=token) when request.data has a “credential” key?
# Does my view raise an InvalidGoogleIdToken exception when ”credential” doesn’t store a valid google OIDC token?
# Does my view NOT call GoogleOIDC.register_new_user when the user already exists?
# Does my view call GoogleOIDC.register_new_user when the user doesn’t exist?
# Is mint_http_tokens called when the user already exists but registers and when a new user is registered?

class GoogleRegistrationTests(TestCase):


    def test_missing_credential_key(self):
        response = self.client.post("/authentication/register/", {'': ''}, content_type="application/json")

        assert response.status_code == 400
        assert response.json()['credential'] == ['This field is required.']

    @patch('authentication.views.mint_http_tokens')
    @patch('authentication.services.GoogleOIDC.register_new_user')
    @patch('authentication.views.get_user_by_oidc_sub')
    @patch('authentication.services.GoogleOIDC.verify_token')
    def test_registration_for_new_user(self, mock_verify_token, mock_get_user, mock_register, mock_mint):
        mock_verify_token.return_value = {
            'sub': '123456789',
            'name': 'Test User',
            'email': 'test@example.com',
        }
        mock_get_user.return_value = None  # user doesn't exist yet

        response = self.client.post("/authentication/register/", {"credential": "fake_token"}, content_type="application/json")

        # verify_token should be called with the credential from the payload
        mock_verify_token.assert_called_once_with(token="fake_token")

        # should check if user exists
        mock_get_user.assert_called_once_with('123456789', 'google')

        # since user doesn't exist, register_new_user should be called
        mock_register.assert_called_once()

        # verify that mint_http_tokens is called
        mock_mint.assert_called_once()

        # should return 201 for new registration
        assert response.status_code == 201

        # response should contain "access" key for access token (set_minted_cookie works properly)
        assert "access" in response.json()


    @patch('authentication.views.mint_http_tokens')
    @patch('authentication.services.GoogleOIDC.register_new_user')
    @patch('authentication.views.get_user_by_oidc_sub')
    @patch('authentication.services.GoogleOIDC.verify_token')
    def test_registration_for_existing_user(self, mock_verify_token, mock_get_user, mock_register, mock_mint):
        mock_verify_token.return_value = {
            'sub': '123456789',
            'name': 'Test User',
            'email': 'test@example.com',
        }
        
        # mock_get_user.return_value = True  # user already exists
        # mock_get_user automatically returns a MagicMock object, safer to leave as this incase attributes are accessed on user.

        response = self.client.post("/authentication/register/", {"credential": "fake_token"}, content_type="application/json")

        # verify_token should be called with the credential from the payload
        mock_verify_token.assert_called_once_with(token="fake_token")

        # should check if user exists
        mock_get_user.assert_called_once_with('123456789', 'google')

        # since user exists, register_new_user should not be called
        mock_register.assert_not_called()

        # verify that mint_http_tokens is called
        mock_mint.assert_called_once()

        # should return 200 for logging existing user in
        assert response.status_code == 200

        # response should contain "access" key for access token (set_minted_cookie works properly)
        assert "access" in response.json()

    
    @patch('authentication.views.mint_http_tokens')
    @patch('authentication.services.GoogleOIDC.register_new_user')
    @patch('authentication.views.get_user_by_oidc_sub')
    @patch('authentication.services.GoogleOIDC.verify_token')
    def test_invalid_credential_token(self, mock_verify_token, mock_get_user, mock_register, mock_mint):
        
        mock_verify_token.side_effect = InvalidGoogleIdToken("bad token")

        response = self.client.post("/authentication/register/", {"credential": "fake_token"}, content_type="application/json")

        # verify response status code is 400 for client error response 
        assert response.status_code == 400
        
        # verify that we reached our except block due to InvalidGoogleIdToken exception and that the detail matches expectations
        assert response.json()["detail"] == "Invalid ID token"
        
        # verify we did not get past GoogleOIDC.verify_token(token=token)
        mock_get_user.assert_not_called()
        
        mock_register.assert_not_called()

        mock_mint.assert_not_called()