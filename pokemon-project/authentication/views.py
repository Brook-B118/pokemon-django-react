from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from google.oauth2 import id_token
from google.auth.transport import requests



@api_view(["POST"])
def register(request):
