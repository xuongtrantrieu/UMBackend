from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import User

class UserAdmin(ModelAdmin):
    list_display = ['email', 'first_name', 'last_name']
    ordering = ['first_name']

admin.site.register(User, UserAdmin)
