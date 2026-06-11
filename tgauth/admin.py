from django.contrib import admin
from .models import TelegramLoginCode


@admin.register(TelegramLoginCode)
class TelegramLoginCodeAdmin(admin.ModelAdmin):
    list_display  = ('code', 'tg_name', 'tg_username', 'verified', 'expires_at', 'created_at')
    list_filter   = ('verified',)
    readonly_fields = ('code', 'telegram_id', 'tg_name', 'tg_username',
                       'verified', 'expires_at', 'created_at')
