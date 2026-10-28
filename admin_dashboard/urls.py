from django.urls import path
from admin_dashboard import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_overview, name='overview'),
    path('inventory/', views.inventory_list, name='inventory'),
    path('inventory/add-pet/', views.add_pet_view, name='add_pet'),
    path('inventory/add-category/', views.add_category_view, name='add_category'),
    path('inventory/add-breed/', views.add_breed_view, name='add_breed'),
    path('orders/', views.orders_management, name='orders'),
    path('orders/<str:order_number>/', views.order_detail_admin, name='order_detail'),
    path('reviews/', views.review_moderation_queue, name='review_moderation'),
    path('dispatch/', views.delivery_dispatch_console, name='delivery_dispatch'),
]
