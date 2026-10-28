from core.models import SiteSetting

def site_context(request):
    try:
        settings = SiteSetting.get_settings()
    except Exception:
        settings = None

    categories = []
    try:
        from catalog.models import PetCategory
        categories = PetCategory.objects.filter(is_active=True).prefetch_related('breeds')
    except Exception:
        pass

    return {
        'site_settings': settings,
        'nav_categories': categories,
        'BUSINESS_NAME': getattr(settings, 'business_name', 'Prestige Paws NYC'),
        'BUSINESS_PHONE': getattr(settings, 'phone', '(212) 555-PAWS'),
        'BUSINESS_EMAIL': getattr(settings, 'email', 'concierge@prestigepaws.nyc'),
        'BUSINESS_ADDRESS': getattr(settings, 'address', '450 Lexington Avenue, Suite 1800, New York, NY 10017'),
    }
