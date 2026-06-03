from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
import requests
from .services import get_cards, add_favorite, delete_favorite
from .selectors import get_user_favorites, get_favorited_card_ids
from .serializers import CardSearchSerializer, FavoriteCardSerializer, FavoriteCardDeleteSerializer
from .throttles import AnonCardSearchRateThrottle, UserCardSearchRateThrottle


# Create your views here.
class CardSearchApi(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonCardSearchRateThrottle, UserCardSearchRateThrottle]

    def get(self, request):
        serializer = CardSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            cards = get_cards(serializer.validated_data)

            if request.user.is_authenticated:
                card_ids = [card['id'] for card in cards]
                # Find which of these cards the user favorited
                favorites = get_favorited_card_ids(user=request.user, searched_card_ids=card_ids)
                for card in cards:
                    if card['id'] in favorites:
                        card['favorited'] = True
                    else:
                        card['favorited'] = False
            else:
                for card in cards:
                    card['favorited'] = False
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


class CardFavoriteApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # User opens their favorites tab
        favorites = get_user_favorites(user=request.user)
        return Response(favorites)
       


    def post(self, request):
        serializer = FavoriteCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            created = add_favorite(user=request.user, data=serializer.validated_data)

            status_code = 201 if created else 200

            return Response({"message": "Card favorited successfully"}, status=status_code)
        
        except Exception:
            return Response({"error": "Unable to favorite card"}, status=500)


    def delete(self, request):
        serializer = FavoriteCardDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            deleted = delete_favorite(user=request.user, data=serializer.validated_data)

            if deleted:
                return Response({"message": "Favorited card removed successfully"}, status=200)
            else:
                return Response({"error": "Unable to remove favorite card"}, status=404)
        except Exception:
            return Response({"error": "Unable to remove favorite card"}, status=500)

