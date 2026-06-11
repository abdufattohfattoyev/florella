from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.utils import timezone


def robots_txt(request):
    return HttpResponse(
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /auth/\n"
        "Disallow: /orders/\n\n"
        "Sitemap: https://florella-cafe.uz/sitemap.xml\n",
        content_type="text/plain",
    )


def sitemap_xml(request):
    today = timezone.now().date().isoformat()
    return HttpResponse(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url>\n'
        f'    <loc>https://florella-cafe.uz/</loc>\n'
        f'    <lastmod>{today}</lastmod>\n'
        f'    <changefreq>daily</changefreq>\n'
        f'    <priority>1.0</priority>\n'
        f'  </url>\n'
        '</urlset>\n',
        content_type="application/xml",
    )


def google_verify(request):
    return HttpResponse(
        "google-site-verification: googleb4718b94f5496dc1.html",
        content_type="text/html",
    )


urlpatterns = [
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap_xml),
    path('googleb4718b94f5496dc1.html', google_verify),
    path('admin/', admin.site.urls),
    path('', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('auth/', include('tgauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
