from django.urls import path

from . import views

urlpatterns = [
    path('search/', views.SearchCardsAPI.as_view(), name="search_cards"),
    path('favorites/', views.FavoriteCardsAPI.as_view(), name="favorite_cards")
]
