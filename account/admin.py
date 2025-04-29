#account/admin.py

from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'organization', 'building', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'organization', 'building', 'role'),
        }),
    )
    list_display = ('email', 'organization', 'building', 'role', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('organization', 'role', 'building', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'organization__name', 'building__name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')
