from django.urls import path
from orders import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('api/validate-coupon/', views.validate_coupon_api, name='validate_coupon_api'),
    path('order/confirmation/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
    path('accounts/orders/', views.order_history_view, name='order_history'),
    path('accounts/orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('accounts/orders/<str:order_number>/receipt/', views.download_receipt_view, name='download_receipt'),
]
