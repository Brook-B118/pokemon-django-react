from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from google.oauth2 import id_token
from google.auth.transport import requests

from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from config.env import env


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    WEB_CLIENT_ID = env('WEB_CLIENT_ID')
    token = request.data.get("credential")
    print(token)
    if not token:
        return Response({"detail": "Missing credential"}, status=400)
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
        userid = idinfo['sub']
        return Response("valid ID token", status=200)
    except ValueError as e:
        return Response({"detail": "Invalid ID token", "error": str(e)}, status=400)
