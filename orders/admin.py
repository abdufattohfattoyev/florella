from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'quantity', 'price', 'subtotal_fmt')
    fields          = ('menu_item', 'quantity', 'price', 'subtotal_fmt')
    can_delete = False

    @admin.display(description='Жами')
    def subtotal_fmt(self, obj):
        return format_html('<b>{} сўм</b>', f'{int(obj.subtotal):,}')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display   = ('id', 'customer_name', 'phone_link', 'delivery_badge',
                      'location_btn', 'status_badge', 'total_fmt', 'created_at')
    list_filter    = ('status', 'delivery_type', 'payment_type', 'created_at')
    list_editable  = ()
    search_fields  = ('customer_name', 'customer_phone', 'delivery_address')
    readonly_fields = ('total_price', 'created_at', 'updated_at', 'latitude', 'longitude')
    inlines        = [OrderItemInline]
    date_hierarchy = 'created_at'
    list_per_page  = 20
    ordering       = ('-created_at',)

    fieldsets = (
        ('Holat va tur', {'fields': ('status', 'delivery_type', 'payment_type')}),
        ('Mijoz ma\'lumotlari', {'fields': ('customer_name', 'customer_phone', 'delivery_address', 'latitude', 'longitude')}),
        ('Qo\'shimcha', {'fields': ('note', 'total_price'), 'classes': ('collapse',)}),
        ('Vaqt', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    STATUS_COLORS = {
        'new':        ('#3498db', '🔵 Янги'),
        'confirmed':  ('#9b59b6', '🟣 Тасдиқланди'),
        'preparing':  ('#f39c12', '🟡 Тайёрланмоқда'),
        'ready':      ('#27ae60', '🟢 Тайёр'),
        'on_the_way': ('#e67e22', '🚗 Йўлда'),
        'delivered':  ('#2ecc71', '✅ Топширилди'),
        'cancelled':  ('#e74c3c', '🔴 Бекор'),
    }

    @admin.display(description='Ҳолат', ordering='status')
    def status_badge(self, obj):
        color, label = self.STATUS_COLORS.get(obj.status, ('#999', obj.status))
        return format_html(
            '<span style="color:{};font-weight:600;">{}</span>',
            color, label
        )

    @admin.display(description='Сумма', ordering='total_price')
    def total_fmt(self, obj):
        return format_html('<b style="color:#27ae60;">{} сўм</b>', f'{int(obj.total_price):,}')

    @admin.display(description='Тур', ordering='delivery_type')
    def delivery_badge(self, obj):
        if obj.delivery_type == 'delivery':
            return format_html('<span style="color:#e31e24;font-weight:700;">🛵 Yetkazib</span>')
        return format_html('<span style="color:#27ae60;font-weight:700;">🚶 Olib ketish</span>')

    @admin.display(description='Телефон', ordering='customer_phone')
    def phone_link(self, obj):
        digits = ''.join(ch for ch in obj.customer_phone if ch.isdigit() or ch == '+')
        return format_html(
            '<a href="tel:{}" style="font-weight:600;white-space:nowrap;">📞 {}</a>',
            digits, obj.customer_phone
        )

    @admin.display(description='Манзил / Стол')
    def location_btn(self, obj):
        if obj.delivery_type != 'delivery':
            if obj.table_number:
                return format_html('Стол №{}', obj.table_number)
            return format_html('<span style="color:#27ae60;font-weight:600;">🚶 Олиб кетади</span>')
        url = obj.google_maps_url
        addr = obj.delivery_address or 'Картада кўриш'
        if len(addr) > 35:
            addr = addr[:32] + '…'
        if not url:
            return '—'
        # GPS bor — aniq nuqta; faqat matn — qidiruv havolasi
        precise = obj.latitude is not None and obj.longitude is not None
        return format_html(
            '<a href="{}" target="_blank" rel="noopener" title="{}"'
            ' style="display:inline-flex;align-items:center;gap:4px;background:{};color:#fff;'
            'font-weight:600;font-size:12px;padding:4px 10px;border-radius:8px;'
            'text-decoration:none;white-space:nowrap;">📍 {}</a>',
            url, obj.delivery_address or '', '#e31e24' if precise else '#7f8c8d', addr
        )

    def get_list_display_links(self, request, list_display):
        return ('id', 'customer_name')
