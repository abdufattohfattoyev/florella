"""Telegram orqali yangi buyurtma haqida adminlarga xabar yuborish.

Sozlash: admin panel -> Buyurtmalar -> Telegram sozlamalari
(token va admin ID lar DB da saqlanadi; bo'sh bo'lsa .env dagi
TELEGRAM_BOT_TOKEN / TELEGRAM_ADMIN_IDS ishlatiladi).

MUHIM: har bir admin botga avval /start bosishi shart, aks holda bot yozolmaydi.
"""
import json
import threading
import urllib.request
import urllib.error
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

API_URL = 'https://api.telegram.org/bot{token}/{method}'


def get_config():
    """(token, [chat_id, ...]) — avval DB, bo'sh bo'lsa .env."""
    from .models import TelegramSettings
    try:
        cfg = TelegramSettings.objects.first()
    except Exception:
        cfg = None

    if cfg is not None:
        if not cfg.enabled:
            return '', []
        token = cfg.bot_token.strip()
        ids = [i.strip() for i in cfg.admin_ids.split(',') if i.strip()]
        if token and ids:
            return token, ids
        # DB chala to'ldirilgan — yetishmagan qismini .env dan olamiz
        if not token:
            token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '').strip()
        if not ids:
            ids = [i.strip() for i in str(getattr(settings, 'TELEGRAM_ADMIN_IDS', '')).split(',') if i.strip()]
        return token, ids

    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '').strip()
    ids = [i.strip() for i in str(getattr(settings, 'TELEGRAM_ADMIN_IDS', '')).split(',') if i.strip()]
    return token, ids


def _api_call(token, method, payload):
    """Telegram API ga so'rov. Natija: javob dict yoki {'ok': False, 'description': ...}."""
    url = API_URL.format(token=token, method=method)
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url, data=data, headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode('utf-8'))
            desc = body.get('description', str(e))
        except Exception:
            desc = str(e)
        logger.warning('Telegram API xatosi (%s): %s', method, desc)
        return {'ok': False, 'description': desc}
    except (urllib.error.URLError, OSError) as e:
        logger.warning('Telegram API xatosi (%s): %s', method, e)
        return {'ok': False, 'description': str(e)}


def _build_message(order):
    pay_icon = '💵' if order.payment_type == 'cash' else '💳'
    lines = [
        f'🆕 <b>Yangi buyurtma №{order.pk}</b>',
        '',
        f'👤 {order.customer_name}',
        f'📞 {order.customer_phone}',
        f'{pay_icon} {order.get_payment_type_display()}',
    ]
    if order.delivery_type == 'delivery':
        lines.append('🛵 Yetkazib berish')
        if order.delivery_address:
            lines.append(f'📍 {order.delivery_address}')
    else:
        lines.append('🚶 Olib ketish')
        if order.table_number:
            lines.append(f'🪑 Stol №{order.table_number}')
    if order.note:
        lines.append(f'📝 Izoh: {order.note}')

    lines.append('')
    lines.append('🛒 <b>Buyurtma tarkibi:</b>')
    for item in order.items.all():
        lines.append(
            f'  {item.quantity} × {item.menu_item.name} — {int(item.subtotal):,} so\'m'.replace(',', ' ')
        )
    lines.append('')
    lines.append(f'💰 <b>Jami: {int(order.total_price):,} so\'m</b>'.replace(',', ' '))
    return '\n'.join(lines)


def _send(order_id):
    # Thread ichida obyektni qayta o'qiymiz — items to'liq saqlangan bo'ladi
    from .models import Order
    try:
        order = Order.objects.prefetch_related('items__menu_item').get(pk=order_id)
    except Order.DoesNotExist:
        return

    token, chat_ids = get_config()
    if not token or not chat_ids:
        return

    text = _build_message(order)
    maps_url = order.google_maps_url
    keyboard = None
    if maps_url:
        keyboard = {'inline_keyboard': [[
            {'text': '📍 Xaritada ochish (Google Maps)', 'url': maps_url}
        ]]}

    for chat_id in chat_ids:
        payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        if keyboard:
            payload['reply_markup'] = keyboard
        _api_call(token, 'sendMessage', payload)

        # Aniq GPS bo'lsa — Telegram'ning o'z lokatsiya pinini ham yuboramiz
        if order.latitude is not None and order.longitude is not None:
            _api_call(token, 'sendLocation', {
                'chat_id': chat_id,
                'latitude': float(order.latitude),
                'longitude': float(order.longitude),
            })


def send_order_notification(order):
    """Buyurtmani fonda (alohida thread'da) yuborish — sayt sekinlashmaydi."""
    token, chat_ids = get_config()
    if not token or not chat_ids:
        return
    threading.Thread(target=_send, args=(order.pk,), daemon=True).start()


def send_test_message():
    """Admin paneldagi 'Test yuborish' tugmasi uchun. Natija: (ok, xabar)."""
    token, chat_ids = get_config()
    if not token:
        return False, "Bot token kiritilmagan."
    if not chat_ids:
        return False, "Admin ID kiritilmagan."

    ok_ids, errors = [], []
    for chat_id in chat_ids:
        resp = _api_call(token, 'sendMessage', {
            'chat_id': chat_id,
            'text': '✅ Florella Cafe bot muvaffaqiyatli ulandi!\n'
                    'Endi yangi buyurtmalar shu yerga keladi.',
        })
        if resp.get('ok'):
            ok_ids.append(chat_id)
        else:
            errors.append(f"{chat_id}: {resp.get('description', 'nomaʼlum xato')}")

    if ok_ids and not errors:
        return True, f"Test xabar yuborildi: {', '.join(ok_ids)}"
    if ok_ids:
        return True, f"Yuborildi: {', '.join(ok_ids)}. Xatolar — {'; '.join(errors)}"
    return False, '; '.join(errors) or 'Xabar yuborilmadi.'
