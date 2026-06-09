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

    customer_name = models.CharField(max_length=200, verbose_name='Mijoz ismi')
    customer_phone = models.CharField(max_length=20, verbose_name='Telefon')
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPE_CHOICES, default='delivery', verbose_name='Buyurtma turi')
    delivery_address = models.TextField(blank=True, default='', verbose_name='Yetkazish manzili')
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
