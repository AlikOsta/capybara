from django.db import models
import os
from slugify import slugify
from django.urls import reverse
from django.contrib.auth import get_user_model


# Модель объявления
class Product(models.Model):

    STATUS_CHOICES = [
        (0, 'Не проверено'),
        (1, 'Одобрено'),
        (2, 'Отклонено'),
        (3, 'Опубликовано'),
        (4, 'Архив'),
    ]

    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='Автор')
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория')
    title = models.CharField(max_length=50, unique=True, verbose_name='Товар')
    description = models.TextField(max_length=350, verbose_name='Описание')
    image = models.ImageField(upload_to='media/images/', verbose_name='Изображение')
    price = models.IntegerField(verbose_name='Цена')
    currency = models.ForeignKey('Currency', null=True, on_delete=models.PROTECT, verbose_name='Валюта')
    city = models.ForeignKey('City', null=True, on_delete=models.PROTECT, verbose_name='Город')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='Статус')
 
    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("app:product_detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name_plural = "Объявления"
        verbose_name = "Объявление"
        ordering = ['-updated_at']


# Модель категории
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Категория')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')
    slug = models.SlugField(max_length=200, verbose_name='Слаг')
    image = models.ImageField(upload_to='media/images/cat_img/', blank=True, null=True, verbose_name='Изображение')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("app:category_detail", args=[self.slug])
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order']


# Модель для валют
class Currency(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name="Название")
    code = models.CharField(max_length=8, db_index=True, verbose_name="Код")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Валюты"
        verbose_name = "Валюта"
        ordering = ['order']


# Модель для городов
class City(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name="Название")

    def __str__(self):
        return self.name