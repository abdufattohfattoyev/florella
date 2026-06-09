from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_type',
            field=models.CharField(
                choices=[('delivery', 'Yetkazib berish'), ('dine_in', 'Restoranda')],
                default='delivery',
                max_length=10,
                verbose_name='Buyurtma turi',
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.TextField(blank=True, default='', verbose_name='Yetkazish manzili'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('new', 'Yangi'),
                    ('confirmed', 'Tasdiqlandi'),
                    ('preparing', 'Tayyorlanmoqda'),
                    ('ready', 'Tayyor'),
                    ('on_the_way', "Yo'lda"),
                    ('delivered', 'Yetkazildi'),
                    ('cancelled', 'Bekor qilindi'),
                ],
                default='new',
                max_length=20,
                verbose_name='Holat',
            ),
        ),
    ]
