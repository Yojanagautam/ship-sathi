from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'college', 'xp', 'reliability_score', 'is_anonymous_mode']
    search_fields = ['email', 'username', 'college']
    ordering = ['email']
    fieldsets = UserAdmin.fieldsets + (
        ('Ship Sathi Info', {
            'fields': ('college', 'is_anonymous_mode', 'reliability_score', 'xp')
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'current_streak', 'longest_streak']
    search_fields = ['user__email', 'display_name']