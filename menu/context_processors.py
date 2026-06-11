import json
from decimal import Decimal
from .models import MenuItem


class _DecEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


def upsell_items(request):
    items = (
        MenuItem.objects
        .filter(is_available=True)
        .select_related('category')
        .values('id', 'name', 'price', 'category__slug', 'image')
    )
    data = [
        {
            'id':       i['id'],
            'name':     i['name'],
            'price':    float(i['price']),
            'category': i['category__slug'],
            'image':    i['image'] or '',
        }
        for i in items
    ]
    return {'upsell_items_json': json.dumps(data, cls=_DecEncoder)}
