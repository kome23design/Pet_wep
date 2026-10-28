from django.urls import path
from pages import views

app_name = 'pages'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('animal-welfare-standards/', views.welfare_standards_view, name='welfare_standards'),
    path('adoption-ownership-info/', views.adoption_info_view, name='adoption_info'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('blog/', views.blog_list_view, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    path('faq/', views.faq_view, name='faq'),
    path('contact/', views.contact_view, name='contact'),
    path('health-documentation-policy/', views.health_policy_view, name='health_policy'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_policy_view, name='terms_policy'),
    path('refund-cancellation-policy/', views.refund_policy_view, name='refund_policy'),
    path('newsletter/subscribe/', views.newsletter_subscribe_api, name='newsletter_subscribe'),
]
