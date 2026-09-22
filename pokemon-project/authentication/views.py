from rest_framework.response import Response
from .services import GoogleOIDC, InvalidGoogleIdToken, mint_http_tokens
from .selectors import get_user_by_oidc_sub
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt import exceptions
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.cache import cache
from django.conf import settings
import secrets

REFRESH_TOKEN_TTL_SECONDS = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())


def create_csrf_token(user_id):
    csrf_token = str(secrets.token_hex(32))

    cache_key = f"csrf_token:{user_id}"
    cache.set(cache_key, csrf_token, timeout=REFRESH_TOKEN_TTL_SECONDS)
    return csrf_token


def set_minted_cookie(refresh_token_object, csrf_token, return_status):
    response = Response(
            {"access": str(refresh_token_object.access_token), "csrf_token": csrf_token},
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="X-App-CSRFToken",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
            )
        ]
    )
    
    def post(self, request):
         
        refresh_str = request.COOKIES.get("refresh_token")
        if refresh_str:
            try:
                reconstructed_refresh_object = RefreshToken(refresh_str)

                # Find user via token's user id
                User = get_user_model()
                user_id = reconstructed_refresh_object["user_id"]

                # Verify CSRF token matches
                cache_key = f"csrf_token:{user_id}"

                try:
                    cached_results = cache.get(cache_key)
                    csrf_token = cached_results
                    if cached_results is not None:
                        if cached_results == request.headers.get("X-App-CSRFToken", ""):
                            user = User.objects.get(pk=user_id)
                            reconstructed_refresh_object.blacklist()
                            
                            new_refresh_token_object = mint_http_tokens(user)
                            cache.set(cache_key, csrf_token, timeout=REFRESH_TOKEN_TTL_SECONDS)
                            
                            response = set_minted_cookie(new_refresh_token_object, csrf_token, status.HTTP_200_OK)
            
                            return response

                        else:
                            return Response(status=403)
                    else:
                        return Response(status=401)
                except Exception:
                    return Response({"detail": "Unable to verify session"}, status=500)

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
                user_id = user.id
                csrf_token = create_csrf_token(user_id)
                refresh_token_object = mint_http_tokens(user)
                response = set_minted_cookie(refresh_token_object, csrf_token, status.HTTP_200_OK)

                return response

            else:
                # register user to model then generate token
                identity = GoogleOIDC.register_new_user(userInfo, "google")
                user_id = identity.user.id
                csrf_token = create_csrf_token(user_id)
                refresh_token_object = mint_http_tokens(identity.user)
                response = set_minted_cookie(refresh_token_object, csrf_token, status.HTTP_201_CREATED)

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
                user_id = user.pk
                csrf_token = create_csrf_token(user_id)
                refresh_token_object = mint_http_tokens(user)
                response = set_minted_cookie(refresh_token_object, csrf_token, status.HTTP_200_OK)

                return response

            else: # if None returned instead of user
                return Response({"detail": "Unauthorized user, need to register."}, status=404)
                # could maybe do a redirect to register route but I think its better to return 404 code and inform the user their account wasn't found in our database.

        except InvalidGoogleIdToken as e: 
            return Response({"detail": "Invalid ID token", "error": str(e)}, status=400)
            

        