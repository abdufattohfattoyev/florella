import json
from decimal import Decimal
from django.conf import settings
from .models import MenuItem


def upsell_items(request):
    items = (
        MenuItem.objects
        .filter(is_available=True)
        .select_related('category')
        .values('id', 'name', 'price', 'category__slug', 'image')
    )
    media = settings.MEDIA_URL  # '/media/'
    data = [
        {
            'id':       i['id'],
            'name':     i['name'],
            'price':    float(i['price']),
            'category': i['category__slug'],
            'image':    (media + i['image']) if i['image'] else '',
        }
        for i in items
    ]
    return {'upsell_items_json': json.dumps(data)}
