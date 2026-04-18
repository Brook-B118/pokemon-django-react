from rest_framework.response import Response
from .services import GoogleOIDC, InvalidGoogleIdToken, mint_http_tokens
from .selectors import get_user_by_oidc_sub
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework_simplejwt.tokens import RefreshToken

def set_minted_cookie(refresh_token_object, return_status):
    response = Response(
            {"access": str(refresh_token_object.access_token)},
            status=return_status,
        )
    
    response.set_cookie(
            key="refresh_token",
            value=str(refresh_token_object),
            httponly=True,
            secure=False,      # True in prod (HTTPS). In local dev you may need False.
            samesite="Lax",   # Often OK for same-site SPA. "None" requires secure=True.
            path="/api/token/refresh/",  # optional but nice
        )
    
    return response

class GoogleRegisterApi(APIView):
    permission_classes = [AllowAny] 
    class InputSerializer(serializers.Serializer):
        credential = serializers.CharField() # Haven't actually made the model yet, this was just for testing purposes.
 
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["credential"]
        
        try:
            # Class for handling the business logic of verifying the token?
            userInfo = GoogleOIDC.verify_token(token=token)
            # TODO: If verified token and user's sub doesn't exist in db yet, maybe call GoogleOidc register method?

            sub = userInfo['sub']
            user = get_user_by_oidc_sub(sub, "google")
            if user: # check if user exists in db already.
                # My idea:
                refresh_token_object = mint_http_tokens(user)
                response = set_minted_cookie(refresh_token_object, status.HTTP_200_OK)

                return response

            else:
                # register user to model then generate token
                identity = GoogleOIDC.register_new_user(userInfo, "google")
                refresh_token_object = mint_http_tokens(identity.user)
                response = set_minted_cookie(refresh_token_object, status.HTTP_201_CREATED)

                return response
        except InvalidGoogleIdToken as e: # I think the class method could return the ValueError right?
            return Response({"detail": "Invalid ID token", "error": str(e)}, status=400)