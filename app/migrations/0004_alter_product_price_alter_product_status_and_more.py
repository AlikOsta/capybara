# Generated by Django 5.1.7 on 2025-03-26 20:32

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_product_title'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(db_index=True, verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.IntegerField(choices=[(0, 'Не проверено'), (1, 'Одобрено'), (2, 'Отклонено'), (3, 'Опубликовано'), (4, 'Архив')], db_index=True, default=0, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(db_index=True, max_length=50, verbose_name='Товар'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['title', 'status'], name='app_product_title_d76bd0_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category', 'status'], name='app_product_categor_a7290b_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['price', 'status'], name='app_product_price_c9d26d_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['created_at', 'status'], name='app_product_created_258ad9_idx'),
        ),
    ]
