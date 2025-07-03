from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'role', 'first_name', 'last_name', 'is_mover', 'is_customer', 'is_staff', 'is_active')
    list_filter = ('role', 'is_mover', 'is_customer', 'is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {
            'fields': ('profile_image', 'gender', 'dob')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Account Details'), {
            'fields': ('role', 'is_mover', 'is_customer')
        }),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_mover', 'is_customer', 'is_active', 'is_staff'),
        }),
    )
