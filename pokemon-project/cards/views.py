from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
import requests
from .services import get_cards
from .serializers import CardSearchSerializer

# Create your views here.
class SearchCardsAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = CardSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            cards = get_cards(serializer.validated_data)
            return Response(cards)
        except requests.exceptions.Timeout:
            return Response(
                {"error": "Card search timed out. Please try again."},
                status=504
            )
        except requests.exceptions.RequestException:
            return Response(
                {"error": "Unable to fetch cards. Please try again later."},
                status=502
            )

