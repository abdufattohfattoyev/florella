from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0003_menuitem_price_m_price_l'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='size_s',
            field=models.CharField(blank=True, default='', max_length=30, verbose_name="O'lcham S nomi (masalan: 20 sm)"),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='size_m',
            field=models.CharField(blank=True, default='', max_length=30, verbose_name="O'lcham M nomi (masalan: 30 sm)"),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='size_l',
            field=models.CharField(blank=True, default='', max_length=30, verbose_name="O'lcham L nomi (masalan: 40 sm)"),
        ),
    ]
