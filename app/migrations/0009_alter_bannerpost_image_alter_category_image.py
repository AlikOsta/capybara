# Generated by Django 5.1.7 on 2025-05-26 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bannerpost',
            name='image',
            field=models.ImageField(upload_to='banner/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='cat_img/', verbose_name='Изображение'),
        ),
    ]
