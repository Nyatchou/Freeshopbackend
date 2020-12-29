from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
import re
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, status, generics
from .serializers import *
from .validators import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser, JSONParser

from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import permissions

from django.conf import settings


import requests

from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from .tokens import *
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.db import transaction

import pyotp
import base64

from rest_framework.decorators import api_view

from authentication.utils import *
from .constants import *
from django.shortcuts import reverse

User = get_user_model()

email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


class ObtainTokenPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer


class SignUp(APIView):
    # parser_classes = (MultiPartParser,)
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        method='post',
        manual_parameters=[
            openapi.Parameter(
                name='first_name', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="First Name"
            ),
            openapi.Parameter(
                name='last_name', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="Last Name"
            ),
            openapi.Parameter(
                name='username', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="Username"
            ),
            openapi.Parameter(
                name='email', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="Email"
            ),
            openapi.Parameter(
                name='password', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="Password"
            )
        ],
        tags=['auth'],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Sucess"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        }
    )
    @action(methods=['post'], detail=False, permission_classes=[],
            url_path='', url_name='')
    def post(self, request, format='json'):
        try:
            with transaction.atomic():
                validator = SignUpValidator(data=request.data)
                if validator.is_valid():
                    validated_data = validator.validated_data
                    if validated_data['should_verify']:
                        email = request.data['email']
                        user = User.objects.get(email=email)
                        return Response({'should_verify': True,
                                         'user_id': user.id}, status=status.HTTP_200_OK)
                    user = User(
                        first_name=validated_data['first_name'],
                        last_name=validated_data['last_name'],
                        email=validated_data['email'],
                        username=validated_data['username'],
                    )
                    user.set_password(validated_data['password'])
                    user.save()

                    user = registered_user(data=validated_data)
                    send_signup_verificaion_mail(user=user, request=request)
                    return Response(
                        {"message": "Please confirm your email address to complete the registration",
                         "user_id": user.id
                         }, status=status.HTTP_201_CREATED)
                else:
                    return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response('Exception: {}'.format(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Login(APIView):

    permission_classes = (permissions.AllowAny,)
    # parser_classes = (MultiPartParser,)

    @swagger_auto_schema(
        method='post',
        manual_parameters=[
            openapi.Parameter(
                name='login_text', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="username or email"
            ),
            openapi.Parameter(
                name='password', in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description="password"
            )
        ],
        tags=['auth'],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Success"
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Unauthorized"
            ),
        }
    )
    @action(methods=['post'], detail=False, permission_classes=[],)
    def post(self, request, format='json'):
        validator = LoginValidator(data=request.data)
        if validator.is_valid():
            validated_data = validator.validated_data
            if validated_data['should_verify']:
                user_id = validated_data['user_id']
                return Response({'should_verify': True, 'user_id': user_id}, status=status.HTTP_200_OK)
            username = validated_data['username']
            password = validated_data['password']
            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                return Response(get_tokens_plus_user(auth_user, request), status=status.HTTP_200_OK)
            else:
                return Response({'message': "Unauthoried"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'message': "Unauthoried"}, status=status.HTTP_401_UNAUTHORIZED)


class FacebookRestAuth(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

    def get_response(self):
        user = self.user
        user.is_remote_user = True
        user.save()
        return Response(get_tokens_plus_user(user, self.request), status=status.HTTP_200_OK)


class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    basic_auth = False


class GoogleRestAuth(SocialLoginView):
    adapter_class = CustomGoogleOAuth2Adapter
    client_class = OAuth2Client

    def get_response(self):
        user = self.user
        user.is_remote_user = True
        user.save()
        return Response(get_tokens_plus_user(user, self.request), status=status.HTTP_200_OK)
