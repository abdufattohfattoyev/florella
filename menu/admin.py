from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('thumb', 'name', 'slug', 'items_count', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('order',)

    @admin.display(description='Расм')
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:8px;">', obj.image.url)
        return '—'

    @admin.display(description='Таомлар сони')
    def items_count(self, obj):
        count = obj.items.count()
        return format_html('<b>{}</b>', count)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display   = ('thumb', 'name', 'category', 'price_fmt', 'is_available', 'is_popular')
    list_filter    = ('category', 'is_available', 'is_popular')
    list_editable  = ('is_available', 'is_popular')
    search_fields  = ('name', 'description')
    autocomplete_fields = ('category',)
    list_per_page  = 25
    ordering       = ('category__order', 'name')

    fieldsets = (
        ('Асосий', {'fields': ('category', 'name', 'description', 'image')}),
        ('Нарxлар ва ўлчамлар', {
            'fields': ('price', 'size_s', 'price_m', 'size_m', 'price_l', 'size_l'),
            'description': 'Пицца учун S/M/L нарx ва ўлчам номларини киритинг (масалан: 20 см, 30 см, 40 см). Бошқа таомлар учун фақат S кифоя.',
        }),
        ('Ҳолат',  {'fields': ('is_available', 'is_popular')}),
    )

    @admin.display(description='Расм')
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:52px;height:52px;object-fit:cover;border-radius:8px;">', obj.image.url)
        return '—'

    @admin.display(description='Нарх', ordering='price')
    def price_fmt(self, obj):
        return format_html('<b style="color:#f39c12;">{} сўм</b>', f'{int(obj.price):,}')
