from django.contrib import admin
from .models import User
from unfold.admin import ModelAdmin
# Register your models here.

class UserAdmin(ModelAdmin):
    list_display = ('id', 'first_name', 'email', 'is_active', 'is_staff')  # Modifiez selon les champs de votre modèle

admin.site.register(User, UserAdmin)
