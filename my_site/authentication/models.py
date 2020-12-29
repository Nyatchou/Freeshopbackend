from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import datetime
from .constants import *
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

phone_validator = RegexValidator(
    regex=r'^(237)\d{9}$', message="Invalid phone number (e.g 237*********)")


class CustomUser(AbstractUser):
    extra_field = models.CharField(blank=True, max_length=120)
    sex = models.CharField(
        max_length=10,
        choices=SEX_CHOICES, 
    )
    is_remote_user = models.BooleanField(default=False)
    phone_number = PhoneNumberField()
    profil_picture = models.ImageField(blank=True, null=True)
    ville_residence = models.CharField(max_length=100, default='Pas de ville choisie')
    adresse = models.CharField(max_length=100, default='Adresse non précisée')
    # profil_picture = models.ImageField(
    #     upload_to=get_user_profile_path, blank=True, null=True, validators=[validate_file_size, ]


class ConfirmToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    kind = models.CharField(max_length=20, choices=TOKEN_TYPES)
    token_hash = models.BinaryField(blank=True)
    token_epires_at = models.DateTimeField(
        default=datetime.datetime.now)
    extra_data = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('kind', 'user',)
