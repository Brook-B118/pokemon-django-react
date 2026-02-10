from rest_framework.response import Response
from .services import GoogleOIDC, InvalidGoogleIdToken
from .selectors import get_user_by_oidc_sub
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import serializers

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
                pass # generate token?, user already has an account
            else:
                pass # register user to model then generate token
                GoogleOIDC.register_new_user(userInfo, "google")
            return Response("valid ID token", status=200)
        except InvalidGoogleIdToken as e: # I think the class method could return the ValueError right?
            return Response({"detail": "Invalid ID token", "error": str(e)}, status=400)