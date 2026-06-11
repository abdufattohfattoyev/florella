import secrets
import string
from django.db import models
from django.utils import timezone
from datetime import timedelta


def _gen_code():
    """Deep-link uchun token: t.me/bot?start=FLXXXXXXXXXXXXXXXXXX"""
    alphabet = string.ascii_uppercase + string.digits
    return 'FL' + ''.join(secrets.choice(alphabet) for _ in range(18))


class TelegramCustomer(models.Model):
    """Telegram orqali kirgan mijoz profili."""
    telegram_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    name        = models.CharField(max_length=200, blank=True, verbose_name='Ism')
    username    = models.CharField(max_length=100, blank=True, verbose_name='Username')
    phone       = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    address     = models.TextField(blank=True, default='', verbose_name='Manzil')
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name="Ro'yxatdan o'tgan")
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mijoz'
        verbose_name_plural = 'Mijozlar'
        ordering = ['-created_at']

    def __str__(self):
        return self.name or f'@{self.username}' or str(self.telegram_id)

    @property
    def default_address(self):
        """Asosiy manzil (yo'q bo'lsa — oxirgi qo'shilgani)."""
        return (self.addresses.filter(is_default=True).first()
                or self.addresses.first())


class CustomerAddress(models.Model):
    """Mijozning saqlangan manzillari (Uy, Ish, ...)."""
    customer   = models.ForeignKey(TelegramCustomer, on_delete=models.CASCADE,
                                   related_name='addresses', verbose_name='Mijoz')
    title      = models.CharField(max_length=100, blank=True, default='',
                                  verbose_name='Nomi', help_text='Masalan: Uy, Ish')
    address    = models.TextField(verbose_name='Manzil')
    latitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                     verbose_name='Kenglik (GPS)')
    longitude  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                     verbose_name='Uzunlik (GPS)')
    is_default = models.BooleanField(default=False, verbose_name='Asosiy manzil')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mijoz manzili'
        verbose_name_plural = 'Mijoz manzillari'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        prefix = f'{self.title}: ' if self.title else ''
        return f'{prefix}{self.address[:50]}'

    def save(self, *args, **kwargs):
        if self.is_default:
            # Bitta mijozda faqat bitta asosiy manzil bo'lsin
            CustomerAddress.objects.filter(
                customer=self.customer, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class TelegramLoginCode(models.Model):
    code        = models.CharField(max_length=64, unique=True, default=_gen_code)
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
