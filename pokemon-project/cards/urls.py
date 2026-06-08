from django.urls import path

from . import views

urlpatterns = [
    path('search/', views.CardSearchApi.as_view(), name="search_cards"),
    path('favorites/', views.CardFavoriteApi.as_view(), name="favorite_cards")
]
