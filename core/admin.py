from django.contrib import admin
from .models import SiteSetting


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'phone', 'email', 'standard_delivery_fee', 'tax_rate', 'enable_payment_simulator')
    search_fields = ('business_name', 'email', 'address')
