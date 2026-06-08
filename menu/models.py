from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Narx (S)')
    price_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Narx (M)')
    price_l = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Narx (L)')
    size_s = models.CharField(max_length=30, blank=True, default='', verbose_name="O'lcham S nomi (masalan: 20 sm)")
    size_m = models.CharField(max_length=30, blank=True, default='', verbose_name="O'lcham M nomi (masalan: 30 sm)")
    size_l = models.CharField(max_length=30, blank=True, default='', verbose_name="O'lcham L nomi (masalan: 40 sm)")
    image = models.ImageField(upload_to='menu/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Taom'
        verbose_name_plural = 'Taomlar'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.price} so'm"
