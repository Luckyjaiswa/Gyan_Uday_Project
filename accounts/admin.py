from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('username', 'email', 'get_full_name', 'role', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering      = ('first_name', 'last_name')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Contact', {
            'fields': ('role', 'phone', 'date_of_birth', 'address', 'profile_picture')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Contact', {
            'fields': ('first_name', 'last_name', 'email', 'role', 'phone')
        }),
    )
