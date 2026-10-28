from django.urls import path
from deliveries import views

app_name = 'deliveries'

urlpatterns = [
    path('track/<str:tracking_number>/', views.live_tracking_view, name='live_tracking'),
    path('api/telemetry/<str:tracking_number>/', views.delivery_telemetry_api, name='telemetry_api'),
    path('courier/portal/', views.courier_portal_view, name='courier_portal'),
    path('courier/update/<str:tracking_number>/', views.update_delivery_location_api, name='courier_update_location'),
]
