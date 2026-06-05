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
    list_display   = ('id', 'customer_name', 'customer_phone', 'table_number',
                      'status_badge', 'total_fmt', 'created_at')
    list_filter    = ('status', 'created_at')
    list_editable  = ('table_number',)
    search_fields  = ('customer_name', 'customer_phone')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    inlines        = [OrderItemInline]
    date_hierarchy = 'created_at'
    list_per_page  = 20
    ordering       = ('-created_at',)

    fieldsets = (
        ('Мижоз', {'fields': ('customer_name', 'customer_phone', 'table_number')}),
        ('Буюртма', {'fields': ('status', 'note', 'total_price')}),
        ('Вақт', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    STATUS_COLORS = {
        'new':       ('#3498db', '🔵 Янги'),
        'confirmed': ('#9b59b6', '🟣 Тасдиқланди'),
        'preparing': ('#f39c12', '🟡 Тайёрланмоқда'),
        'ready':     ('#27ae60', '🟢 Тайёр'),
        'delivered': ('#2ecc71', '✅ Топширилди'),
        'cancelled': ('#e74c3c', '🔴 Бекор'),
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

    def get_list_display_links(self, request, list_display):
        return ('id', 'customer_name')
