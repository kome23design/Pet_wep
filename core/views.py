from django.shortcuts import render
from django.http import HttpResponse

def custom_404(request, exception=None):
    return render(request, 'core/404.html', status=404)

def custom_500(request):
    return render(request, 'core/500.html', status=500)

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /portal/",
        "Disallow: /accounts/",
        "Disallow: /checkout/",
        "Disallow: /cart/",
        "Disallow: /admin/",
        "Allow: /",
        "",
        "Sitemap: https://royalmaltipoos.shop/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def sitemap_xml(request):
    from catalog.models import Pet, PetBreed, PetCategory
    categories = PetCategory.objects.filter(is_active=True)
    breeds = PetBreed.objects.filter(is_active=True)
    pets = Pet.objects.filter(is_published=True, status='available')

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Static public pages
    urls = [
        '/', '/about/', '/animal-welfare-standards/', '/adoption-ownership-info/',
        '/pets/', '/reviews/', '/gallery/', '/blog/', '/faq/', '/contact/',
        '/health-documentation-policy/', '/privacy-policy/', '/terms-and-conditions/'
    ]
    for u in urls:
        xml.append(f"  <url><loc>https://royalmaltipoos.shop{u}</loc><priority>0.8</priority></url>")
        
    for c in categories:
        xml.append(f"  <url><loc>https://royalmaltipoos.shop/category/{c.slug}/</loc><priority>0.9</priority></url>")
    for b in breeds:
        xml.append(f"  <url><loc>https://royalmaltipoos.shop/collection/{b.slug}/</loc><priority>0.9</priority></url>")
    for p in pets:
        xml.append(f"  <url><loc>https://royalmaltipoos.shop/pet/{p.slug}/</loc><priority>1.0</priority></url>")

    xml.append('</urlset>')
    return HttpResponse("\n".join(xml), content_type="application/xml")
