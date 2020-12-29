from django.contrib.auth import get_user_model
from .models import CustomUser
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.fields import empty
from my_site.settings import MINIMAL_PASSWORD_LENGTH
from authentication.constants import SEX_CHOICES

import re
email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(CustomTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        # token['fav_color'] = user.fav_color
        return token


# ...


class CustomUserBaseSerializer(serializers.ModelSerializer):

    def request_owner(self):
        request = self.context.get('request', None)
        if request:
            return request.user
        return None



class CustomUserSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ('email', 'password' )

        extra_kwargs = {"sex": {"required": False},
                        "username": {"required": False},
                        "profil_picture": {"required": False}}

    def update(self, instance, validated_data):
        # dont update exluded values
        # for field in self.Meta.exclude + ('is_owner', 'is_system_admin', 'is_influencer', 'is_seller', ):
        #     validated_data.pop(field, None)

        sex = validated_data.pop('sex', instance.sex)
        phone_number = validated_data.pop(
            'phone_number', instance.phone_number)
        profil_picture = validated_data.pop(
            'profil_picture', instance.profil_picture)
        username = validated_data.pop('username', instance.username)
        first_name = validated_data.pop('first_name', instance.first_name)
        last_name = validated_data.pop('last_name', instance.last_name)

        setattr(instance, 'sex', sex)
        setattr(instance, 'phone_number', phone_number)
        setattr(instance, 'profil_picture', profil_picture)
        setattr(instance, 'first_name', first_name)
        setattr(instance, 'last_name', last_name)
        setattr(instance, 'username', username)

        return instance


class CustomUserSerializer(CustomUserBaseSerializer):
    email = serializers.EmailField(
        required=True
    )
    username = serializers.CharField()
    password = serializers.CharField(
        min_length=MINIMAL_PASSWORD_LENGTH, write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password', 'id',
                  'profil_picture', 'sex', 'first_name', 'last_name')
        read_only_fields = ('profil_picture', )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # as long as the fields are the same, we can just use this
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ()
        extra_kwargs = {'password': {'write_only': True}}


class SignInValidator(serializers.Serializer):
    provider = serializers.CharField(max_length=4, required=True)
    login_text = serializers.CharField(max_length=30, required=False)

    def validate(self, data):
        if data['login_text']:
            login_text = data['login_text']
            is_email = re.search(email_regex, login_text)
            if is_email:
                try:
                    user = User.objects.get(email=login_text)
                    data['username'] = user.username
                except:
                    pass
            # raise serializers.ValidationError("Login text must not be present")
        return data
