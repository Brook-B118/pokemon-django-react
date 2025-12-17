from rest_framework.response import Response
from .services import GoogleOidc, InvalidGoogleIdToken

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import serializers

class GoogleRegisterApi(APIView):
    permission_classes = [AllowAny]
    # TODO: Add an input serializer class? Note: This should go in the 
    class InputSerializer(serializers.Serializer):
        credential = serializers.CharField() # Haven't actually made the model yet, this was just for testing purposes.
 
    def post(self, request):
        input = self.InputSerializer(data=request.data)
        input.is_valid(raise_exception=True)

        token = input.validated_data["credential"]
        
        # data = request.data
        # token = data.get("credential")
        # if not token:
        #     return Response({"detail": "Missing credential"}, status=400)
        try:
            # Class for handling the business logic of verifying the token?
            userId = GoogleOidc.verify_token(token=token)
            # TODO: If verified token and user's sub doesn't exist in db yet, maybe call GoogleOidc register method?
            return Response("valid ID token", status=200)
        except InvalidGoogleIdToken as e: # I think the class method could return the ValueError right?
            return Response({"detail": "Invalid ID token", "error": str(e)}, status=400)