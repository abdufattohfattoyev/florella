"""
python manage.py tgbot

Bot long polling rejimida ishlaydi — foydalanuvchilarning
FL-XXXX kodlarini qabul qiladi va tizimga kirishni tasdiqlaydi.

Production'da Telegram webhook ishlatish tavsiya etiladi.
"""
import time
import json
import logging
import urllib.request
import urllib.error

from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.telegram import get_config, _api_call

logger = logging.getLogger(__name__)


def _process_update(token, update):
    message = update.get('message') or update.get('edited_message')
    if not message:
        return

    chat_id  = message.get('chat', {}).get('id')
    text     = (message.get('text') or '').strip().upper()
    from_    = message.get('from', {})
    name     = (from_.get('first_name') or '') + (' ' + (from_.get('last_name') or '')).rstrip()
    username = from_.get('username', '')

    if text.startswith('/START'):
        _api_call(token, 'sendMessage', {
            'chat_id': chat_id,
            'text': (
                '👋 Salom! Men Florella Cafe login botiman.\n\n'
                '🔑 Saytdagi FL-XXXX kodini yuboring — tizimga kirasiz.'
            ),
        })
        return

    if text.startswith('FL-') and len(text) == 7:
        from tgauth.models import TelegramLoginCode
        try:
            obj = TelegramLoginCode.objects.get(code=text, verified=False)
        except TelegramLoginCode.DoesNotExist:
            _api_call(token, 'sendMessage', {
                'chat_id': chat_id,
                'text': '❌ Kod topilmadi yoki muddati o\'tgan.\nSaytda yangi kod oling.',
            })
            return

        if obj.is_expired():
            obj.delete()
            _api_call(token, 'sendMessage', {
                'chat_id': chat_id,
                'text': '⏰ Kodning muddati o\'tdi (5 daqiqa).\nSaytda yangi kod oling.',
            })
            return

        obj.telegram_id = chat_id
        obj.tg_name     = name.strip() or str(chat_id)
        obj.tg_username = username
        obj.verified    = True
        obj.save()

        display = f'@{username}' if username else name.strip() or str(chat_id)
        _api_call(token, 'sendMessage', {
            'chat_id': chat_id,
            'text': (
                f'✅ Muvaffaqiyatli! Xush kelibsiz, {display}!\n\n'
                '🛍 Saytga qaytib buyurtma bering: https://florella-cafe.uz'
            ),
        })
        logger.info('Login: %s (chat_id=%s)', display, chat_id)
        return

    _api_call(token, 'sendMessage', {
        'chat_id': chat_id,
        'text': '🤔 Tushunmadim.\n\nSaytdagi FL-XXXX kodini yuboring.',
    })


class Command(BaseCommand):
    help = 'Telegram bot — long polling (local development)'

    def handle(self, *args, **options):
        token, _ = get_config()
        if not token:
            self.stderr.write('❌ Bot token topilmadi. Admin panel → Telegram sozlamalari.')
            return

        # Webhook o'chirish (long polling bilan konflikt bo'lmasligi uchun)
        _api_call(token, 'deleteWebhook', {'drop_pending_updates': False})

        self.stdout.write(self.style.SUCCESS('✅ Bot ishga tushdi. FL-XXXX kodlarini kutmoqda…'))
        self.stdout.write('   To\'xtatish: Ctrl+C\n')

        offset = 0
        while True:
            try:
                url = f'https://api.telegram.org/bot{token}/getUpdates'
                params = json.dumps({
                    'offset': offset,
                    'timeout': 30,
                    'allowed_updates': ['message'],
                }).encode()
                req = urllib.request.Request(
                    url, data=params,
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req, timeout=35) as resp:
                    data = json.loads(resp.read().decode())

                if not data.get('ok'):
                    self.stderr.write(f'API xato: {data}')
                    time.sleep(5)
                    continue

                for update in data.get('result', []):
                    offset = update['update_id'] + 1
                    try:
                        _process_update(token, update)
                    except Exception as e:
                        logger.exception('Update xatosi: %s', e)

            except KeyboardInterrupt:
                self.stdout.write('\n👋 Bot to\'xtatildi.')
                break
            except Exception as e:
                logger.warning('getUpdates xatosi: %s', e)
                time.sleep(5)
