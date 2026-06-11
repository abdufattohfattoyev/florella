from django.conf import settings


def customer_profile(request):
    """Kirgan mijoz profili + Yandex xarita kaliti."""
    ctx = {'yandex_maps_key': getattr(settings, 'YANDEX_MAPS_JS_KEY', '')
                              or getattr(settings, 'YANDEX_GEOCODER_KEY', '')}
    tg_id = request.session.get('tg_id')
    if not tg_id:
        return ctx
    from .models import TelegramCustomer
    try:
        ctx['customer_profile'] = TelegramCustomer.objects.get(telegram_id=tg_id)
    except TelegramCustomer.DoesNotExist:
        pass
    return ctx
