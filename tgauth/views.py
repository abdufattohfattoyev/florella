import json
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from orders.telegram import get_config, _api_call
from .bot_logic import process_message
from .models import TelegramLoginCode, TelegramCustomer, CustomerAddress

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
    """AJAX: yangi token generatsiya qiladi."""
    obj = TelegramLoginCode.create_new()
    token, _ = get_config()
    bot_username = _get_bot_username(token) or 'florellazakaz_bot'
    return JsonResponse({
        'code': obj.code,
        'bot_username': bot_username,
    })


def check_code(request, code):
    """AJAX: token tasdiqlanganini tekshiradi."""
    try:
        obj = TelegramLoginCode.objects.get(code=code)
    except TelegramLoginCode.DoesNotExist:
        return JsonResponse({'status': 'not_found'})
    if obj.is_expired():
        return JsonResponse({'status': 'expired'})
    if obj.verified:
        # Mijoz profilini yaratish yoki yangilash
        customer, created = TelegramCustomer.objects.get_or_create(
            telegram_id=obj.telegram_id,
            defaults={'name': obj.tg_name, 'username': obj.tg_username},
        )
        if not created:
            # Username yangilangan bo'lishi mumkin; ism profilda tahrirlangan bo'lsa saqlanadi
            if obj.tg_username and customer.username != obj.tg_username:
                customer.username = obj.tg_username
            if not customer.name:
                customer.name = obj.tg_name
            customer.save()

        request.session['tg_id']       = obj.telegram_id
        request.session['tg_name']     = customer.name or obj.tg_name
        request.session['tg_username'] = obj.tg_username
        name = customer.name or obj.tg_name
        obj.delete()
        return JsonResponse({'status': 'ok', 'name': name})
    return JsonResponse({'status': 'waiting'})


def logout_view(request):
    request.session.flush()
    return redirect('menu:menu_list')


def profile_view(request):
    """Mijoz profili: tahrirlash + buyurtmalar tarixi."""
    tg_id = request.session.get('tg_id')
    if not tg_id:
        return redirect('tgauth:login')

    customer, _ = TelegramCustomer.objects.get_or_create(
        telegram_id=tg_id,
        defaults={
            'name': request.session.get('tg_name', ''),
            'username': request.session.get('tg_username', ''),
        },
    )

    if request.method == 'POST':
        from django.contrib import messages
        action = request.POST.get('action', 'save_profile')

        if action == 'save_profile':
            name  = (request.POST.get('name') or '').strip()
            phone = (request.POST.get('phone') or '').strip()
            if name:
                customer.name = name
                request.session['tg_name'] = name
            customer.phone = phone
            customer.save()
            messages.success(request, 'Profil saqlandi!')

        elif action == 'add_address':
            title   = (request.POST.get('title') or '').strip()
            street  = (request.POST.get('street') or '').strip()
            house   = (request.POST.get('house') or '').strip()
            podyezd = (request.POST.get('podyezd') or '').strip()
            apt     = (request.POST.get('apartment') or '').strip()

            def _coord(field):
                try:
                    return round(float(request.POST.get(field, '')), 6)
                except (TypeError, ValueError):
                    return None

            if street:
                # To'liq manzil: ko'cha + dom + podyezd + kvartira
                full = street
                if house:
                    full += f', {house}-dom'
                if podyezd:
                    full += f', {podyezd}-podyezd'
                if apt:
                    full += f', {apt}-kvartira'
                CustomerAddress.objects.create(
                    customer=customer, title=title, address=full,
                    latitude=_coord('latitude'), longitude=_coord('longitude'),
                    is_default=not customer.addresses.exists(),
                )
                messages.success(request, 'Manzil qo\'shildi!')

        elif action == 'del_address':
            CustomerAddress.objects.filter(
                pk=request.POST.get('addr_id'), customer=customer
            ).delete()
            messages.success(request, 'Manzil o\'chirildi.')

        elif action == 'set_default':
            addr = CustomerAddress.objects.filter(
                pk=request.POST.get('addr_id'), customer=customer
            ).first()
            if addr:
                addr.is_default = True
                addr.save()
                messages.success(request, f'"{addr.title or addr.address[:30]}" asosiy manzil qilindi.')

        return redirect('tgauth:profile')

    from orders.models import Order
    orders = (
        Order.objects.filter(tg_id=tg_id)
        .prefetch_related('items__menu_item')
        .order_by('-created_at')[:30]
    )

    return render(request, 'tgauth/profile.html', {
        'customer': customer,
        'orders': orders,
        'addresses': customer.addresses.all(),
    })


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

    token, _ = get_config()
    if token:
        try:
            process_message(token, message)
        except Exception as e:
            logger.exception('Webhook xatosi: %s', e)
    return JsonResponse({'ok': True})


def _get_bot_username(token):
    if not token:
        return ''
    try:
        resp = _api_call(token, 'getMe', {})
        return resp.get('result', {}).get('username', '')
    except Exception:
        return ''
