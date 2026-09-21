from rest_framework.response import Response
from .services import GoogleOIDC, InvalidGoogleIdToken, mint_http_tokens
from .selectors import get_user_by_oidc_sub
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt import exceptions
from drf_spectacular.utils import extend_schema


def set_minted_cookie(refresh_token_object, return_status):
    response = Response(
            {"access": str(refresh_token_object.access_token)},
            status=return_status,
        )
    
    response.set_cookie(
            key="refresh_token",
            value=str(refresh_token_object),
            httponly=True,
            secure=True,      # True in prod (HTTPS). In local dev you may need False.
            samesite="Strict",   # Often OK for same-site SPA. "None" requires secure=True.
            path="/api/authentication/token/refresh/",  # optional but nice
        )
    
    return response

class TokenRefreshApi(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
         
        refresh_str = request.COOKIES.get("refresh_token")
        if refresh_str:
            try:
                reconstructed_refresh_object = RefreshToken(refresh_str)

                # Find user via token's user id
                User = get_user_model()
                user_id = reconstructed_refresh_object["user_id"]
                user = User.objects.get(pk=user_id)
                reconstructed_refresh_object.blacklist()

                new_refresh_token_object = mint_http_tokens(user)
                
                response = set_minted_cookie(new_refresh_token_object, status.HTTP_200_OK)

                return response

            except exceptions.TokenError as e:
                return Response({"detail": "Invalid Refresh token", "error": str(e)}, status=401)
        else:
            return Response({"detail": "Missing Refresh token"}, status=401)

class GoogleRegisterApi(APIView):
    permission_classes = [AllowAny] 
    class InputSerializer(serializers.Serializer):
        credential = serializers.CharField() # Haven't actually made the model yet, this was just for testing purposes.

    @extend_schema(
        request=InputSerializer,
    )
 
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["credential"]
        
        try:
            # Class for handling the business logic of verifying the token?
            userInfo = GoogleOIDC.verify_token(token=token)
            sub = userInfo['sub']
            user = get_user_by_oidc_sub(sub, "google")

            if user: # check if user exists in db already.
                refresh_token_object = mint_http_tokens(user)
                response = set_minted_cookie(refresh_token_object, status.HTTP_200_OK)

                return response

            else:
                # register user to model then generate token
                identity = GoogleOIDC.register_new_user(userInfo, "google")
                refresh_token_object = mint_http_tokens(identity.user)
                response = set_minted_cookie(refresh_token_object, status.HTTP_201_CREATED)

                return response
        except InvalidGoogleIdToken as e:
            return Response({"detail": "Invalid ID token", "error": str(e)}, status=400)
        
class GoogleLoginApi(APIView):
    permission_classes = [AllowAny]
    class InputSerializer(serializers.Serializer):
        credential = serializers.CharField()

    @extend_schema(
        request=InputSerializer,
    )

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["credential"]

        try:
            userInfo = GoogleOIDC.verify_token(token=token)
            sub = userInfo['sub']
            user = get_user_by_oidc_sub(sub, "google")

            if user: # check if user exists in db 
                refresh_token_object = mint_http_tokens(user)
                response = set_minted_cookie(refresh_token_object, status.HTTP_200_OK)

                return response

            else: # if None returned instead of user
                return Response({"detail": "Unauthorized user, need to register."}, status=404)
                # could maybe do a redirect to register route but I think its better to return 404 code and inform the user their account wasn't found in our database.

        except InvalidGoogleIdToken as e: 
            return Response({"detail": "Invalid ID token", "error": str(e)}, status=400)
            

        