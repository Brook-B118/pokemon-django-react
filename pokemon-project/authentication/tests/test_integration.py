from django.test import TestCase
from unittest.mock import patch
from rest_framework.response import Response
from ..services import InvalidGoogleIdToken

# If a user actually exists in our database, does my view return a 200 response?
# If a user doesn’t exist in the database when registering, does my view create a user in the database correctly and return a 201 response?
# Does my get_user_by_oidc_sub correctly return None if user doesn’t exist in database?
# Does my get_user_by_oidc_sub correctly return a user object if they exist?
# Does mint_http_tokens actually return valid tokens?