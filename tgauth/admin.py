from django.contrib import admin
from .models import TelegramLoginCode, TelegramCustomer, CustomerAddress


class CustomerAddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 0
    fields = ('title', 'address', 'is_default', 'latitude', 'longitude')


@admin.register(TelegramCustomer)
class TelegramCustomerAdmin(admin.ModelAdmin):
    list_display    = ('name', 'username', 'phone', 'telegram_id', 'created_at')
    search_fields   = ('name', 'username', 'phone')
    readonly_fields = ('telegram_id', 'created_at', 'updated_at')
    inlines         = [CustomerAddressInline]


@admin.register(TelegramLoginCode)
class TelegramLoginCodeAdmin(admin.ModelAdmin):
    list_display  = ('code', 'tg_name', 'tg_username', 'verified', 'expires_at', 'created_at')
    list_filter   = ('verified',)
    readonly_fields = ('code', 'telegram_id', 'tg_name', 'tg_username',
                       'verified', 'expires_at', 'created_at')
