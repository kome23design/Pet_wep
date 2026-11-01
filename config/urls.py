from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from core.views import custom_404, custom_500, robots_txt, sitemap_xml

admin.site.site_header = "Royal Maltipoos Administration — support@royalmaltipoos.shop"
admin.site.site_title = "Royal Maltipoos Admin (royalmaltipoos.shop)"
admin.site.index_title = "Royal Maltipoos Executive Administration | support@royalmaltipoos.shop"

urlpatterns = [
    # Browser URL Favicon
    path('favicon.ico', RedirectView.as_view(url='/static/images/royal_maltipoos_logo.png', permanent=False), name='favicon'),

    # Built-in Django Admin
    path('admin/', admin.site.urls),
    
    # Custom Staff & Executive Management Portal
    path('portal/', include('admin_dashboard.urls')),
    
    # Apps
    path('', include('pages.urls')),
    path('', include('catalog.urls')),
    path('cart/', include('cart.urls')),
    path('', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('deliveries/', include('deliveries.urls')),
    path('reviews/', include('reviews.urls')),
    path('accounts/', include('accounts.urls')),
    
    # SEO & Crawlers
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap_xml, name='sitemap_xml'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'
