from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, CustomerProfile, CustomerAddress, DeliveryAgentProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Prestige Paws Role & Phone', {'fields': ('role', 'phone_number', 'is_verified', 'avatar')}),
    )

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_contact_method', 'residence_type', 'has_fenced_yard')

@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_label', 'recipient_name', 'city', 'state', 'postal_code', 'is_default')
    list_filter = ('state', 'is_default')

@admin.register(DeliveryAgentProfile)
class DeliveryAgentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge_number', 'vehicle_make_model', 'vehicle_license_plate', 'is_on_duty', 'last_gps_update')
    list_filter = ('is_on_duty',)
