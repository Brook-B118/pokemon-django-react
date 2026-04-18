from django.urls import path

from . import views

urlpatterns = [
    # path("", views.index, name="index"), # localhost:8000/authentication/
    # Note: views.index doesn't work here because our views file doesn't have a view called 'index' yet.
    # path expects two args, the route and a view for the route.
    # path("xyz", views.xyz, name="example_path") # localhost:8000/authentication/xyz
    # Note: views.xyz works here because our views file has a route called 'xyz'
    path('register/', views.GoogleRegisterApi.as_view(), name="register_openid_user"),
    path('token/refresh/', views.TokenRefresh.as_view(), name="use_refresh_token_for_new_access_token")
]
