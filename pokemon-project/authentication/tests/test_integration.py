from django.test import TestCase
from unittest.mock import patch
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from ..services import GoogleOIDC, InvalidGoogleIdToken
from django.contrib.auth import get_user_model
from ..models import OIDCIdentity 
from ..selectors import get_user_by_oidc_sub
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt import exceptions

# If a user actually exists in our database, does my view return a 200 response?
# If a user doesn’t exist in the database when registering, does my view create a user in the database correctly and return a 201 response?
# Does my get_user_by_oidc_sub correctly return None if user doesn’t exist in database?
# Does my get_user_by_oidc_sub correctly return a user object if they exist?
# Does mint_http_tokens actually return valid tokens?

class GoogleRegistrationIntegrationTests(TestCase):
    google_registration_route = "/authentication/register/"


    def setUp(self):
        # this runs before every test method
        User = get_user_model()
        self.user = User.objects.create(
            username='test_user',
            email='test@example.com',
        )
        self.user.set_unusable_password()
        self.user.save()

        OIDCIdentity.objects.create(
            user=self.user,
            provider='google',
            sub='123456789',
        )

    
    # If a user actually exists in our database, does my view return a 200 response with an access token in response.json and the refresh token in the header as a cookie?
    @patch('authentication.services.GoogleOIDC.verify_token')
    def test_login_an_existing_user_trying_to_register(self, mock_verify_token):
        mock_verify_token.return_value = {
            'name':'test_user',
            'email':'test@example.com',
            'sub': '123456789'
        }

        response = self.client.post(self.google_registration_route, {"credential": "fake_token"}, content_type="application/json")

        token = AccessToken(response.json()["access"])

        # verify that access token is in the response
        assert 'access' in response.json()
        # verify the access token contains the correct user id when decoded
        assert token["user_id"] == str(self.user.id)
        # verify the response has a "refresh_token" key
        assert 'refresh_token' in response.cookies
        cookie = response.cookies['refresh_token']
        assert cookie['httponly'] == True
        assert cookie['samesite'] == 'Lax'
        assert cookie['path'] == "/authentication/token/refresh/"
    
    # If a user doesn’t exist in the database when registering, does my view create a user in the database correctly and return a 201 response?
    @patch('authentication.services.GoogleOIDC.verify_token')
    def test_registering_a_new_user(self, mock_verify_token):
        mock_verify_token.return_value = {
            'name':'test_new_user',
            'email':'new_user_test@example.com',
            'sub': '987654321'
        }

        response = self.client.post(self.google_registration_route, {"credential": "fake_token"}, content_type="application/json")

        User = get_user_model()
        new_user = User.objects.get(username='test_new_user')
        assert new_user.email == 'new_user_test@example.com'

        identity = OIDCIdentity.objects.get(sub='987654321')
        assert identity.provider == 'google'
        assert identity.user == new_user

        token = AccessToken(response.json()["access"])

        # verify that access token is in the response
        assert 'access' in response.json()
        # verify the access token contains the correct user id when decoded
        assert token["user_id"] == str(new_user.id)
        # verify the response has a "refresh_token" key
        assert 'refresh_token' in response.cookies
        cookie = response.cookies['refresh_token']
        assert cookie['httponly'] == True
        assert cookie['samesite'] == 'Lax'
        assert cookie['path'] == "/authentication/token/refresh/"


    # Does my get_user_by_oidc_sub correctly return a user object if they exist?
    def test_get_user_by_oidc_sub_with_existing_user(self):
        result = get_user_by_oidc_sub("123456789", "google")
        assert result == self.user

    # Does my get_user_by_oidc_sub correctly return None if user doesn’t exist in database?
    def test_get_user_by_oidc_sub_with_user_that_does_not_exist_yet(self):
        result = get_user_by_oidc_sub("0101010110", "google")
        assert result == None


class GoogleLoginIntegrationTests(TestCase):
    google_login_route = "/authentication/login/"

    def setUp(self):
        # this runs before every test method
        User = get_user_model()
        self.user = User.objects.create(
            username='test_user',
            email='test@example.com',
        )
        self.user.set_unusable_password()
        self.user.save()

        OIDCIdentity.objects.create(
            user=self.user,
            provider='google',
            sub='123456789',
        )

    @patch('authentication.services.GoogleOIDC.verify_token')
    def test_login_an_existing_user(self, mock_verify_token):
        mock_verify_token.return_value = {
            'name':'test_user',
            'email':'test@example.com',
            'sub': '123456789'
        }

        response = self.client.post(self.google_login_route, {"credential": "fake_token"}, content_type="application/json")

        token = AccessToken(response.json()["access"])

        # verify that access token is in the response
        assert 'access' in response.json()
        assert response.status_code == 200
        # verify the access token contains the correct user id when decoded
        assert token["user_id"] == str(self.user.id)
        # verify the response has a "refresh_token" key
        assert 'refresh_token' in response.cookies
        cookie = response.cookies['refresh_token']
        assert cookie['httponly'] == True
        assert cookie['samesite'] == 'Lax'
        assert cookie['path'] == "/authentication/token/refresh/"

    
    @patch('authentication.services.GoogleOIDC.verify_token')
    def test_login_an_unregistered_user(self, mock_verify_token):
        mock_verify_token.return_value = {
            'name':'test_unregistered_user',
            'email':'unregisteredtest@example.com',
            'sub': '432512201'
        }

        response = self.client.post(self.google_login_route, {"credential": "fake_token"}, content_type="application/json")

        assert response.status_code == 404
        assert response.json()["detail"] == "Unauthorized user, need to register."

class RefreshTokenIntegrationTests(TestCase):
    refresh_token_route = "/authentication/token/refresh/"

    def setUp(self):
        # this runs before every test method
        User = get_user_model()
        self.user = User.objects.create(
            username='test_user',
            email='test@example.com',
        )
        self.user.set_unusable_password()
        self.user.save()

        OIDCIdentity.objects.create(
            user=self.user,
            provider='google',
            sub='123456789',
        )

        self.refresh_token_str = str(RefreshToken.for_user(self.user))

    def test_valid_refresh_token(self):
        self.client.cookies["refresh_token"] = self.refresh_token_str
        response = self.client.post(self.refresh_token_route)

        token = AccessToken(response.json()["access"])
        assert 'access' in response.json()
        # verify the access token contains the correct user id when decoded
        assert token["user_id"] == str(self.user.id)
    
    def test_invalid_refresh_token(self):
        self.client.cookies["refresh_token"] = "invalid_refresh_token"
        response = self.client.post(self.refresh_token_route)

        assert response.json()["detail"] == "Invalid Refresh token"
        assert response.status_code == 401