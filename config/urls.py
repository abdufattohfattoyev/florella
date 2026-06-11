import json
import urllib.parse
import urllib.request

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
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


def yandex_verify(request):
    return HttpResponse(
        "<html>\n"
        "    <head>\n"
        '        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n'
        "    </head>\n"
        "    <body>Verification: 9b61f8e28b2e9825</body>\n"
        "</html>",
        content_type="text/html",
    )


def geocode_reverse(request):
    """Koordinata -> manzil. Avval Yandex (uy raqamigacha aniq), keyin OSM zaxira."""
    try:
        lat = float(request.GET.get('lat', ''))
        lon = float(request.GET.get('lon', ''))
    except (TypeError, ValueError):
        return JsonResponse({'ok': False}, status=400)

    # 1) Yandex Geocoder — O'zbekiston uchun eng to'liq ma'lumot
    ykey = getattr(settings, 'YANDEX_GEOCODER_KEY', '')
    if ykey:
        try:
            url = (
                'https://geocode-maps.yandex.ru/1.x/?'
                + urllib.parse.urlencode({
                    'apikey': ykey,
                    'geocode': f'{lon},{lat}',
                    'format': 'json',
                    'kind': 'house',
                    'results': 1,
                    'lang': 'ru_RU',
                })
            )
            with urllib.request.urlopen(url, timeout=6) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            members = (data.get('response', {}).get('GeoObjectCollection', {})
                       .get('featureMember', []))
            if members:
                geo = members[0]['GeoObject']
                comps = (geo.get('metaDataProperty', {}).get('GeocoderMetaData', {})
                         .get('Address', {}).get('Components', []))
                parts = {c['kind']: c['name'] for c in comps}
                street = parts.get('street') or parts.get('district') or ''
                house = parts.get('house', '')
                locality = parts.get('locality') or parts.get('area') or ''
                addr_parts = [p for p in [street, parts.get('district') if parts.get('district') != street else '', locality] if p]
                return JsonResponse({
                    'ok': True,
                    'source': 'yandex',
                    'address': ', '.join(addr_parts[:3]) or geo.get('name', ''),
                    'street': street,
                    'house': house,
                })
        except Exception:
            pass

    # 2) Nominatim (OSM) — zaxira
    try:
        url = (
            'https://nominatim.openstreetmap.org/reverse?'
            + urllib.parse.urlencode({
                'format': 'json', 'zoom': 18, 'addressdetails': 1,
                'lat': lat, 'lon': lon, 'accept-language': 'uz,ru',
            })
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'FlorellaCafe/1.0'})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        a = data.get('address', {})
        street = a.get('road') or a.get('pedestrian') or a.get('residential') or ''
        parts = []
        if street:
            parts.append(street)
        if a.get('suburb') or a.get('neighbourhood') or a.get('quarter'):
            parts.append(a.get('suburb') or a.get('neighbourhood') or a.get('quarter'))
        if a.get('city') or a.get('town') or a.get('village'):
            parts.append(a.get('city') or a.get('town') or a.get('village'))
        address = ', '.join(parts[:3]) if parts else \
            ', '.join((data.get('display_name') or '').split(',')[:3])
        return JsonResponse({
            'ok': True,
            'source': 'osm',
            'address': address,
            'street': street,
            'house': a.get('house_number', ''),
        })
    except Exception:
        return JsonResponse({'ok': False})


urlpatterns = [
    path('geo/reverse/', geocode_reverse),
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap_xml),
    path('googleb4718b94f5496dc1.html', google_verify),
    path('yandex_9b61f8e28b2e9825.html', yandex_verify),
    path('admin/', admin.site.urls),
    path('', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('auth/', include('tgauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
