from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0002_category_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='price_m',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Narx (M)'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='price_l',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Narx (L)'),
        ),
    ]
