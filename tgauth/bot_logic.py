"""Bot xabarlarini qayta ishlash — webhook va long polling uchun umumiy logika."""
import logging

from orders.telegram import _api_call

logger = logging.getLogger(__name__)

SITE_URL = 'https://florella-cafe.uz'

SITE_KEYBOARD = {'inline_keyboard': [[
    {'text': "🛍 Saytga o'tish", 'url': SITE_URL}
]]}


def process_message(bot_token, message):
    """Telegram'dan kelgan bitta xabarni qayta ishlaydi."""
    chat_id = message.get('chat', {}).get('id')
    raw     = (message.get('text') or '').strip()
    from_   = message.get('from', {})
    name    = ((from_.get('first_name') or '') + ' ' + (from_.get('last_name') or '')).strip()
    username = from_.get('username', '')

    if not chat_id or not raw:
        return

    # /start TOKEN — saytdan kelgan deep-link (bir bosishda login)
    if raw.lower().startswith('/start'):
        parts = raw.split(maxsplit=1)
        login_token = parts[1].strip() if len(parts) > 1 else ''
        if login_token:
            _try_login(bot_token, chat_id, login_token, name, username)
        else:
            _api_call(bot_token, 'sendMessage', {
                'chat_id': chat_id,
                'text': (
                    '👋 Salom! Men Florella Cafe botiman.\n\n'
                    "Tizimga kirish uchun saytdagi «Telegram orqali kirish» "
                    'tugmasini bosing — qolganini men bajaraman. 😊'
                ),
                'reply_markup': SITE_KEYBOARD,
            })
        return

    # Eski usul: FL-XXXX kod matn sifatida yuborilgan (zaxira yo'l)
    code = raw.upper()
    if code.startswith('FL'):
        _try_login(bot_token, chat_id, code, name, username)
        return

    _api_call(bot_token, 'sendMessage', {
        'chat_id': chat_id,
        'text': (
            "🤔 Tushunmadim.\n\n"
            "Tizimga kirish uchun saytdagi «Telegram orqali kirish» tugmasini bosing."
        ),
        'reply_markup': SITE_KEYBOARD,
    })


def _try_login(bot_token, chat_id, login_token, name, username):
    from .models import TelegramLoginCode

    try:
        obj = TelegramLoginCode.objects.get(code=login_token, verified=False)
    except TelegramLoginCode.DoesNotExist:
        _api_call(bot_token, 'sendMessage', {
            'chat_id': chat_id,
            'text': "❌ Havola eskirgan yoki noto'g'ri.\nSaytdan qaytadan urinib ko'ring.",
            'reply_markup': SITE_KEYBOARD,
        })
        return

    if obj.is_expired():
        obj.delete()
        _api_call(bot_token, 'sendMessage', {
            'chat_id': chat_id,
            'text': "⏰ Havolaning muddati o'tdi (5 daqiqa).\nSaytdan qaytadan urinib ko'ring.",
            'reply_markup': SITE_KEYBOARD,
        })
        return

    obj.telegram_id = chat_id
    obj.tg_name     = name or str(chat_id)
    obj.tg_username = username
    obj.verified    = True
    obj.save()

    display = f'@{username}' if username else (name or str(chat_id))
    _api_call(bot_token, 'sendMessage', {
        'chat_id': chat_id,
        'text': (
            f'✅ Muvaffaqiyatli kirdingiz, {display}!\n\n'
            'Saytga qayting — buyurtma berishingiz mumkin. 🍣'
        ),
        'reply_markup': SITE_KEYBOARD,
    })
    logger.info('Telegram login: %s (chat_id=%s)', display, chat_id)
