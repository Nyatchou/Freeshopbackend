from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display+('sex',)
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Fields", {'fields': (
            'sex',
            'phone_number'
            )}),
        ("Social", {'fields': (
            'profil_picture',
            )}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ConfirmToken)
