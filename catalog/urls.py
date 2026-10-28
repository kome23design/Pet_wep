from django.urls import path
from catalog import views

app_name = 'catalog'

urlpatterns = [
    path('pets/', views.pet_list_view, name='pet_list'),
    path('category/<slug:category_slug>/', views.category_detail_view, name='category_detail'),
    path('category/<slug:category_slug>/<slug:breed_slug>/', views.breed_detail_view, name='breed_detail'),
    path('collection/<slug:breed_slug>/', views.breed_detail_view, name='collection_detail'),
    path('pet/<slug:slug>/', views.pet_detail_view, name='pet_detail'),
    path('search/', views.search_view, name='search'),
]
