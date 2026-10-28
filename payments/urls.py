from django.urls import path
from payments import views

app_name = 'payments'

urlpatterns = [
    path('stripe/checkout/<str:order_number>/', views.stripe_checkout_view, name='stripe_checkout'),
    path('simulate/<str:order_number>/', views.simulate_payment_view, name='simulate_payment'),
    path('stripe/webhook/', views.stripe_webhook_view, name='stripe_webhook'),
    path('stripe/return/<str:order_number>/', views.payment_return_view, name='payment_return'),
    path('stripe/cancel/<str:order_number>/', views.payment_cancel_view, name='payment_cancel'),
]
