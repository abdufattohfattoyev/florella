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
    list_display   = ('id', 'customer_name', 'customer_phone', 'delivery_badge',
                      'address_short', 'status_badge', 'total_fmt', 'created_at')
    list_filter    = ('status', 'delivery_type', 'created_at')
    list_editable  = ()
    search_fields  = ('customer_name', 'customer_phone', 'delivery_address')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    inlines        = [OrderItemInline]
    date_hierarchy = 'created_at'
    list_per_page  = 20
    ordering       = ('-created_at',)

    fieldsets = (
        ('Мижоз', {'fields': ('customer_name', 'customer_phone')}),
        ('Буюртма', {'fields': ('delivery_type', 'delivery_address', 'table_number', 'status', 'note', 'total_price')}),
        ('Вақт', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
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
            return format_html('<span style="color:#e31e24;font-weight:700;">🛵 Ета</span>')
        return format_html('<span style="color:#27ae60;font-weight:700;">🍽️ Зал</span>')

    @admin.display(description='Манзил / Стол')
    def address_short(self, obj):
        if obj.delivery_type == 'delivery':
            addr = obj.delivery_address or '—'
            return format_html('<span title="{}">{}</span>', addr, addr[:40] + ('…' if len(addr) > 40 else ''))
        if obj.table_number:
            return format_html('Стол №{}', obj.table_number)
        return '—'

    def get_list_display_links(self, request, list_display):
        return ('id', 'customer_name')
