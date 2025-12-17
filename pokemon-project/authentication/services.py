from config.env import env
from google.oauth2 import id_token
from google.auth.transport import requests

WEB_CLIENT_ID = env('WEB_CLIENT_ID')

class InvalidGoogleIdToken(Exception):
    pass

class GoogleOidc:

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

            userId = idinfo['sub']
            return userId
        
        except ValueError as e:
            # return dict({"detail": "Invalid ID token", "error": str(e)}, status=400)
            raise InvalidGoogleIdToken(str(e)) from e
        
        # TODO: Create selector file for looking up if the user's sub already exists?
        # TODO: Should I keep a register method in here that gets called when token is verified?
        #