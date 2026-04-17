from config.env import env
from google.oauth2 import id_token
from google.auth.transport import requests
from .models import OIDCIdentity
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

WEB_CLIENT_ID = env('WEB_CLIENT_ID')

def mint_http_tokens(user):
    refresh_and_access = RefreshToken.for_user(user)
    return refresh_and_access


class InvalidGoogleIdToken(Exception):
    pass

class GoogleOIDC:
    @staticmethod
    def verify_token(token):
        # print(token)
        try:
            # Specify the WEB_CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                WEB_CLIENT_ID)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [WEB_CLIENT_ID_1, WEB_CLIENT_ID_2, WEB_CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            # If the request specified a Google Workspace domain
            # if idinfo['hd'] != DOMAIN_NAME:
            #     raise ValueError('Wrong domain name.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            # This ID is unique to each Google Account, making it suitable for use as a primary key
            # during account lookup. Email is not a good choice because it can be changed by the user.

            # userId = idinfo['sub']
            userInfo = idinfo
            return userInfo
        
        except ValueError as e:
            # return dict({"detail": "Invalid ID token", "error": str(e)}, status=400)
            raise InvalidGoogleIdToken(str(e)) from e
        
        # Created selector file for looking up if the user's sub already exists.

    @staticmethod
    @transaction.atomic
    def register_new_user(userInfo, provider):
        User = get_user_model()
        # for user we can name, i don't think we can do email.
        user = User.objects.create(
            username=userInfo['name'], # change this to be something else, eventually users can edit this.
            email=userInfo['email'], # Include email in scope when requesting openId token from google.
        )
        user.set_unusable_password()
        user.save()
        # for OIDCIdentity we can give the provider and sub.
        identity = OIDCIdentity.objects.create(
            user=user,
            provider=provider,
            sub=userInfo['sub']
            )
        return identity