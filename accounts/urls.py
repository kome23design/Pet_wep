from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('addresses/', views.address_book_view, name='addresses'),
    path('addresses/add/', views.add_address_view, name='address_add'),
    path('addresses/<int:pk>/edit/', views.edit_address_view, name='address_edit'),
    path('addresses/<int:pk>/delete/', views.delete_address_view, name='address_delete'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:pet_id>/', views.toggle_wishlist_view, name='wishlist_toggle'),
    path('password-reset/', views.password_reset_request_view, name='password_reset'),
]
