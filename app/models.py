from django.db import models
from slugify import slugify
from django.urls import reverse


# Модель объявления
class Product(models.Model):

    STATUS_CHOICES = [
        (0, 'Не проверено'),
        (1, 'Одобрено'),
        (2, 'Отклонено'),
        (3, 'Опубликовано'),
        (4, 'Архив'),
    ]

    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория')
    title = models.CharField(max_length=50, unique=True, verbose_name='Товар')
    description = models.TextField(max_length=350, verbose_name='Описание')
    image = models.ImageField(upload_to='media/images/', verbose_name='Изображение')
    price = models.FloatField(verbose_name='Цена')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Слаг')
    currency = models.ForeignKey('Currency', null=True, on_delete=models.PROTECT, verbose_name='Валюта')
    city = models.ForeignKey('SubLocation', null=True, on_delete=models.PROTECT, verbose_name='Город')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='Статус')
 
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("app:post_detail", args=[self.slug])

    class Meta:
        verbose_name_plural = "Объявления"
        verbose_name = "Объявление"
        ordering = ['-updated_at']


# Модель категории
class Category(models.Model):
    title = models.CharField(max_length=50, unique=True, verbose_name='Категория')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Слаг')
    image = models.ImageField(upload_to='media/images/cat_img/', blank=True, verbose_name='Изображение')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
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
class SubLocation(models.Model):
    title = models.CharField(max_length=50, db_index=True, verbose_name="Название")