from django.contrib import admin
from .models import Delivery, DeliveryLocation, DeliveryEvent


class DeliveryLocationInline(admin.TabularInline):
    model = DeliveryLocation
    extra = 0
    readonly_fields = ('recorded_at',)
    ordering = ('-recorded_at',)


class DeliveryEventInline(admin.TabularInline):
    model = DeliveryEvent
    extra = 0
    readonly_fields = ('event_time',)
    ordering = ('-event_time',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'order', 'status', 'assigned_agent', 'current_location_label', 'updated_at')
    list_filter = ('status', 'carrier_type', 'created_at')
    search_fields = ('tracking_number', 'order__order_number', 'assigned_agent__username', 'current_location_label')
    readonly_fields = ('tracking_number', 'created_at', 'updated_at')
    inlines = [DeliveryLocationInline, DeliveryEventInline]
