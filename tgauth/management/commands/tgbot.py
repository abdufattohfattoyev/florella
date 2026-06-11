"""
python manage.py tgbot

Bot long polling rejimida ishlaydi — lokal ishlab chiqish uchun.

DIQQAT: bu buyruq webhook'ni o'chiradi! Production'da webhook ishlatilsa,
lokal test tugagach webhook'ni qayta o'rnating:
  python manage.py tgbot --set-webhook
"""
import time
import json
import logging
import urllib.request

from django.core.management.base import BaseCommand

from orders.telegram import get_config, _api_call
from tgauth.bot_logic import process_message, SITE_URL

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Telegram bot — long polling (lokal) yoki webhook o\'rnatish'

    def add_arguments(self, parser):
        parser.add_argument(
            '--set-webhook', action='store_true',
            help=f'Webhook o\'rnatish ({SITE_URL}/auth/webhook/) va chiqish',
        )

    def handle(self, *args, **options):
        token, _ = get_config()
        if not token:
            self.stderr.write('❌ Bot token topilmadi. Admin panel → Telegram sozlamalari.')
            return

        if options['set_webhook']:
            resp = _api_call(token, 'setWebhook', {
                'url': f'{SITE_URL}/auth/webhook/',
                'allowed_updates': ['message'],
            })
            if resp.get('ok'):
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Webhook o\'rnatildi: {SITE_URL}/auth/webhook/\n'
                    '   Endi bot serverda alohida jarayonsiz ishlaydi.'
                ))
            else:
                self.stderr.write(f'❌ Xato: {resp.get("description")}')
            return

        # Long polling — webhook bilan konflikt bo'lmasligi uchun o'chiramiz
        _api_call(token, 'deleteWebhook', {'drop_pending_updates': False})

        self.stdout.write(self.style.SUCCESS('✅ Bot ishga tushdi (long polling).'))
        self.stdout.write(self.style.WARNING(
            '⚠️  Webhook o\'chirildi! Production uchun keyin qayta o\'rnating:\n'
            '   python manage.py tgbot --set-webhook'
        ))
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
                    message = update.get('message') or update.get('edited_message')
                    if not message:
                        continue
                    try:
                        process_message(token, message)
                    except Exception as e:
                        logger.exception('Update xatosi: %s', e)

            except KeyboardInterrupt:
                self.stdout.write('\n👋 Bot to\'xtatildi.')
                break
            except Exception as e:
                logger.warning('getUpdates xatosi: %s', e)
                time.sleep(5)
