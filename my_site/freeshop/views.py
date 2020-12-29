from django.shortcuts import render
from rest_framework import response
from rest_framework.authtoken.models import Token

# Create your views here.
# def redirect_view(request):
#     user = self.request.user
#     token = Token.objects.get_or_create(user=user)
#     return response.Response({'token': token.key})
from rest_framework.views import APIView

class Auth(APIView):

    def get(self, request, format=None):
        user = self.request.user
        if user.is_anonymous:
            return response.Response({'info':"Vous n'êtes pas (plus) connecté"})
        token, _ = Token.objects.get_or_create(user=user)
        return response.Response({'key': token.key})
        