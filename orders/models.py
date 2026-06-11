from django.db import models
from menu.models import MenuItem


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('confirmed', 'Tasdiqlandi'),
        ('preparing', 'Tayyorlanmoqda'),
        ('ready', 'Tayyor'),
        ('on_the_way', "Yo'lda"),
        ('delivered', 'Yetkazildi'),
        ('cancelled', 'Bekor qilindi'),
    ]
    DELIVERY_TYPE_CHOICES = [
        ('delivery', 'Yetkazib berish'),
        ('dine_in', 'Olib ketish'),
    ]
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Naqt pul'),
        ('card', 'Karta'),
    ]

    tg_id = models.BigIntegerField(null=True, blank=True, db_index=True, verbose_name='Telegram ID')
    customer_name = models.CharField(max_length=200, verbose_name='Mijoz ismi')
    customer_phone = models.CharField(max_length=20, verbose_name='Telefon')
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPE_CHOICES, default='delivery', verbose_name='Buyurtma turi')
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, default='cash', verbose_name="To'lov turi")
    delivery_address = models.TextField(blank=True, default='', verbose_name='Yetkazish manzili')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Kenglik (GPS)')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Uzunlik (GPS)')
    table_number = models.PositiveIntegerField(blank=True, null=True, verbose_name='Stol raqami')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Holat')
    note = models.TextField(blank=True, verbose_name='Izoh')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Jami narx')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
        ordering = ['-created_at']

    def __str__(self):
        return f"Buyurtma #{self.pk} - {self.customer_name}"

    def calculate_total(self):
        self.total_price = sum(item.subtotal for item in self.items.all())
        self.save()

    @property
    def google_maps_url(self):
        if self.latitude is not None and self.longitude is not None:
            return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        if self.delivery_address:
            from urllib.parse import quote
            return f"https://www.google.com/maps/search/?api=1&query={quote(self.delivery_address)}"
        return ''

    @property
    def osm_embed_url(self):
        if self.latitude is None or self.longitude is None:
            return ''
        lat, lon = float(self.latitude), float(self.longitude)
        return (
            "https://www.openstreetmap.org/export/embed.html"
            f"?bbox={lon - 0.005}%2C{lat - 0.003}%2C{lon + 0.005}%2C{lat + 0.003}"
            f"&layer=mapnik&marker={lat}%2C{lon}"
        )


class TelegramSettings(models.Model):
    """Telegram bot sozlamalari — admin paneldan boshqariladi (bitta yozuv)."""
    enabled = models.BooleanField(default=True, verbose_name='Yoqilgan',
                                  help_text="O'chirsangiz xabar yuborilmaydi")
    bot_token = models.CharField(max_length=120, blank=True, verbose_name='Bot token',
                                 help_text="@BotFather dan olingan token (123456:ABC-DEF...)")
    admin_ids = models.CharField(max_length=300, blank=True, verbose_name='Admin ID lar',
                                 help_text="@userinfobot dan olingan ID. Bir nechta bo'lsa vergul bilan: 111,222. "
                                           "Har bir admin botga avval /start bosishi shart!")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Telegram sozlamalari'
        verbose_name_plural = 'Telegram sozlamalari'

    def __str__(self):
        return 'Telegram bot sozlamalari'

    def save(self, *args, **kwargs):
        self.pk = 1  # doim bitta yozuv
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT, verbose_name='Taom')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Miqdor')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Narx')

    class Meta:
        verbose_name = 'Buyurtma elementi'
        verbose_name_plural = 'Buyurtma elementlari'

    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity}"

    @property
    def subtotal(self):
        return (self.price or 0) * self.quantity
