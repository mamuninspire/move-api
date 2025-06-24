from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'get_email', 'get_full_name', 'bio', 'address')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('customer_id',)

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
