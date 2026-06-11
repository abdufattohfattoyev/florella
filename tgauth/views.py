import json
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from orders.telegram import get_config, _api_call
from .models import TelegramLoginCode

logger = logging.getLogger(__name__)


def login_view(request):
    if request.session.get('tg_id'):
        return redirect('menu:menu_list')
    obj = TelegramLoginCode.create_new()
    token, _ = get_config()
    bot_username = _get_bot_username(token) or 'florellazakaz_bot'
    return render(request, 'tgauth/login.html', {
        'code': obj.code,
        'bot_username': bot_username,
    })


def new_code(request):
    """AJAX: yangi kod generatsiya qiladi."""
    obj = TelegramLoginCode.create_new()
    token, _ = get_config()
    bot_username = _get_bot_username(token) or 'florellazakaz_bot'
    return JsonResponse({
        'code': obj.code,
        'bot_username': bot_username,
    })


def check_code(request, code):
    """AJAX: kod tasdiqlanganini tekshiradi."""
    try:
        obj = TelegramLoginCode.objects.get(code=code)
    except TelegramLoginCode.DoesNotExist:
        return JsonResponse({'status': 'not_found'})
    if obj.is_expired():
        return JsonResponse({'status': 'expired'})
    if obj.verified:
        request.session['tg_id']       = obj.telegram_id
        request.session['tg_name']     = obj.tg_name
        request.session['tg_username'] = obj.tg_username
        obj.delete()
        return JsonResponse({'status': 'ok', 'name': obj.tg_name})
    return JsonResponse({'status': 'waiting'})


def logout_view(request):
    request.session.flush()
    return redirect('menu:menu_list')


@csrf_exempt
@require_POST
def bot_webhook(request):
    """Telegram webhook — bot xabarlarini qabul qiladi."""
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'ok': True})

    message = data.get('message') or data.get('edited_message')
    if not message:
        return JsonResponse({'ok': True})

    chat_id = message.get('chat', {}).get('id')
    text    = (message.get('text') or '').strip().upper()
    from_   = message.get('from', {})
    name    = (from_.get('first_name') or '') + (' ' + (from_.get('last_name') or '')).rstrip()
    username = from_.get('username', '')

    token, _ = get_config()
    if not token:
        return JsonResponse({'ok': True})

    # /start komandasi — yordam xabari
    if text.startswith('/START'):
        _api_call(token, 'sendMessage', {
            'chat_id': chat_id,
            'text': (
                '👋 Salom! Men Florella Cafe login botiman.\n\n'
                'Saytdagi kodni (masalan: FL-1234) yuboring — tizimga kirasiz.'
            ),
        })
        return JsonResponse({'ok': True})

    # FL-XXXX formatidagi kod
    if text.startswith('FL-') and len(text) == 7:
        try:
            obj = TelegramLoginCode.objects.get(code=text, verified=False)
        except TelegramLoginCode.DoesNotExist:
            _api_call(token, 'sendMessage', {
                'chat_id': chat_id,
                'text': '❌ Kod topilmadi yoki muddati o\'tgan. Saytda yangi kod oling.',
            })
            return JsonResponse({'ok': True})

        if obj.is_expired():
            obj.delete()
            _api_call(token, 'sendMessage', {
                'chat_id': chat_id,
                'text': '⏰ Kodning muddati o\'tdi (5 daqiqa). Saytda yangi kod oling.',
            })
            return JsonResponse({'ok': True})

        obj.telegram_id = chat_id
        obj.tg_name     = name.strip() or str(chat_id)
        obj.tg_username = username
        obj.verified    = True
        obj.save()

        display = f'@{username}' if username else name.strip() or str(chat_id)
        _api_call(token, 'sendMessage', {
            'chat_id': chat_id,
            'text': f'✅ Muvaffaqiyatli! Florella Cafe ga xush kelibsiz, {display}!\n\nSaytga qaytib buyurtma bering.',
        })
        return JsonResponse({'ok': True})

    # Noto'g'ri xabar
    _api_call(token, 'sendMessage', {
        'chat_id': chat_id,
        'text': '🤔 Tushunmadim. Saytdagi FL-XXXX kodini yuboring.',
    })
    return JsonResponse({'ok': True})


def _get_bot_username(token):
    if not token:
        return ''
    try:
        resp = _api_call(token, 'getMe', {})
        return resp.get('result', {}).get('username', '')
    except Exception:
        return ''
