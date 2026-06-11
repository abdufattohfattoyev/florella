from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from menu.models import MenuItem
from .models import Order, OrderItem
from .telegram import send_order_notification
import json


def order_create(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        delivery_type = request.POST.get('delivery_type', 'delivery')
        delivery_address = request.POST.get('delivery_address', '').strip()
        payment_type = request.POST.get('payment_type', 'cash')

        def _coord(name):
            try:
                return round(float(request.POST.get(name, '')), 6)
            except (TypeError, ValueError):
                return None

        latitude = _coord('latitude') if delivery_type == 'delivery' else None
        longitude = _coord('longitude') if delivery_type == 'delivery' else None
        table_number = request.POST.get('table_number') or None
        note = request.POST.get('note', '')
        cart = json.loads(request.POST.get('cart', '[]'))

        if not cart:
            messages.error(request, 'Savatcha bo\'sh! Kamida bitta taom tanlang.')
            return redirect('menu:menu_list')

        tg_id = request.session.get('tg_id')

        order = Order.objects.create(
            tg_id=tg_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            delivery_type=delivery_type,
            delivery_address=delivery_address,
            latitude=latitude,
            longitude=longitude,
            payment_type=payment_type,
            table_number=table_number,
            note=note,
        )

        for entry in cart:
            menu_item = get_object_or_404(MenuItem, pk=entry['id'])
            cart_price = entry.get('price') or menu_item.price
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=entry['quantity'],
                price=cart_price,
            )

        order.calculate_total()

        # Mijoz profilini oxirgi ma'lumotlar bilan yangilash
        if tg_id:
            from tgauth.models import TelegramCustomer, CustomerAddress
            customer, _ = TelegramCustomer.objects.update_or_create(
                telegram_id=tg_id,
                defaults={
                    'name': customer_name or '',
                    'phone': customer_phone or '',
                },
            )
            # Ishlatilgan manzilni saqlangan manzillarga qo'shish (takror bo'lmasin)
            if delivery_type == 'delivery' and delivery_address:
                addr, _ = CustomerAddress.objects.get_or_create(
                    customer=customer,
                    address=delivery_address,
                    defaults={'latitude': latitude, 'longitude': longitude},
                )
                addr.is_default = True
                if latitude is not None:
                    addr.latitude, addr.longitude = latitude, longitude
                addr.save()

        send_order_notification(order)
        messages.success(request, f'Buyurtmangiz qabul qilindi! #{order.pk}')
        return redirect('orders:order_success', pk=order.pk)

    return redirect('menu:menu_list')


def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/order_success.html', {'order': order})


def order_cancel(request, pk):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        if order.status == 'new':
            order.status = 'cancelled'
            order.save()
            messages.success(request, f'Buyurtma #{order.pk} bekor qilindi.')
        else:
            messages.error(request, 'Bu buyurtmani bekor qilib bo\'lmaydi.')
        return redirect('menu:menu_list')
    return redirect('orders:order_success', pk=pk)
