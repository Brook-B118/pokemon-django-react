from django.urls import path

from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # path("", views.index, name="index"), # localhost:8000/authentication/
    # Note: views.index doesn't work here because our views file doesn't have a view called 'index' yet.
    # path expects two args, the route and a view for the route.
    # path("xyz", views.xyz, name="example_path") # localhost:8000/authentication/xyz
    # Note: views.xyz works here because our views file has a route called 'xyz'
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # don't use this because it requires credentials, but were using OIDC
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # don't use this because it requires credentials, but were using OIDC
    path('register/', views.GoogleRegisterApi.as_view(), name="register_openid_user")
]
