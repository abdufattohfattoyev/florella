from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from menu.models import MenuItem
from .models import Order, OrderItem
import json


def order_create(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        delivery_type = request.POST.get('delivery_type', 'delivery')
        delivery_address = request.POST.get('delivery_address', '')
        payment_type = request.POST.get('payment_type', 'cash')
        table_number = request.POST.get('table_number') or None
        note = request.POST.get('note', '')
        cart = json.loads(request.POST.get('cart', '[]'))

        if not cart:
            messages.error(request, 'Savatcha bo\'sh! Kamida bitta taom tanlang.')
            return redirect('menu:menu_list')

        order = Order.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            delivery_type=delivery_type,
            delivery_address=delivery_address,
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
        messages.success(request, f'Buyurtmangiz qabul qilindi! #{order.pk}')
        return redirect('orders:order_success', pk=order.pk)

    return redirect('menu:menu_list')


def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/order_success.html', {'order': order})
