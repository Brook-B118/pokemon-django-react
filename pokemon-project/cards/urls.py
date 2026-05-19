from django.urls import path

from . import views

urlpatterns = [
    path('search/', views.SearchCardsAPI.as_view(), name="search_cards")
]
