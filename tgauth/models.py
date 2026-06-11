import random
import string
from django.db import models
from django.utils import timezone
from datetime import timedelta


def _gen_code():
    digits = ''.join(random.choices(string.digits, k=4))
    return f'FL-{digits}'


class TelegramLoginCode(models.Model):
    code        = models.CharField(max_length=12, unique=True, default=_gen_code)
    telegram_id = models.BigIntegerField(null=True, blank=True)
    tg_name     = models.CharField(max_length=200, blank=True)
    tg_username = models.CharField(max_length=100, blank=True)
    expires_at  = models.DateTimeField()
    verified    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Telegram login kodi'
        verbose_name_plural = 'Telegram login kodlari'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} — {"✓" if self.verified else "…"}'

    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def create_new(cls):
        cls.objects.filter(expires_at__lt=timezone.now()).delete()
        return cls.objects.create(
            expires_at=timezone.now() + timedelta(minutes=5)
        )
