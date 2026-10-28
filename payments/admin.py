from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'currency', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'currency', 'created_at')
    search_fields = ('order__order_number', 'stripe_payment_intent_id', 'stripe_session_id')
    readonly_fields = ('created_at', 'updated_at')
