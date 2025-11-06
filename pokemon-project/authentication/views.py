from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# Had to include this so the dev server actually runs, but its commented out to prove a point in urls.py
# def index(request):
#     return HttpResponse("test")

# def xyz(request):
#     # processing - database, cache, rendering HTML template
#     return HttpResponse("This is an example of a view")

def register(request):
    # Simple steps involved in registering using JWT:

    # 1. User provides a username 

    # 2. User provides a password

    # 3. They will be asked to login, so aside from hashing a password, there isn't really any JWT relevant
    # work done here.

    pass

def login(request):

    # Simple steps involved in logging in using JWT:

    # 1. User provides username and password
    if request.method == "POST":
        # pretend the login info matches
        pass # I actually don't need to perform username/password checks here because authentication/token/ already uses TokenObtainPairView
             # from rest_framework_simplejwt.views. It already handles serialization and checking username/password.
             # I guess I need to remind myself that this is purely API and not a web server, so I don't need to worry about rendering templates as
             # that is the frontend's job to render the correct page based on successful login or not.

    # 2. Information is checked against database

    # 3. If valid, a JWT is provided to the user and optionally a refresh token (recommended)

    pass