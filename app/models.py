# app/models.py
import os
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from slugify import slugify
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator, MaxValueValidator


class Product(models.Model):
    """
    Модель объявления.
    """

    STATUS_CHOICES = [
        (0, 'Не проверено'),
        (1, 'Одобрено'),
        (2, 'Отклонено'),
        (3, 'Опубликовано'),
        (4, 'Архив'),
    ]

    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='Автор')
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name='Категория')
    title = models.CharField(max_length=50, verbose_name='Товар', db_index=True) 
    description = models.TextField(max_length=350, verbose_name='Описание')
    image = models.ImageField(upload_to='media/images/', verbose_name='Изображение')
    price = models.IntegerField(verbose_name='Цена', db_index=True, validators=[MinValueValidator(0), MaxValueValidator(9999999)],) 
    currency = models.ForeignKey('Currency', null=True, on_delete=models.PROTECT, verbose_name='Валюта')
    city = models.ForeignKey('City', null=True, on_delete=models.PROTECT, verbose_name='Город')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='Статус', db_index=True) 


    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        """
        Переопределённый метод удаления. Удаляет физический файл изображения,
        если он существует, перед вызовом стандартного удаления записи.
        """
        if self.image:
            image_path = self.image.path
            if os.path.isfile(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    pass
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("app:product_detail", kwargs={"pk": self.pk})

    def get_view_count(self):
        """Возвращает количество уникальных просмотров объявления."""
        return self.views.count()
    
    def save(self, *args, **kwargs):
        if self.image and not self.id:  
            
            img = Image.open(self.image)
            
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
            
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            output = BytesIO()
            img.save(output, format="WEBP", quality=65, optimize=True)
            output.seek(0)
            
            base_name = self.image.name.rsplit('.', 1)[0]
            self.image = ContentFile(output.read(), name=f"{base_name}.webp")
        
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['title', 'status']),  
            models.Index(fields=['category', 'status']),  
            models.Index(fields=['price', 'status']), 
            models.Index(fields=['created_at', 'status']),  
        ]


class Category(models.Model):
    """
    Модель категории.
    """
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


class Currency(models.Model):
    """
    Модель для валют.
    """
    name = models.CharField(max_length=20, db_index=True, verbose_name="Название")
    code = models.CharField(max_length=8, db_index=True, verbose_name="Код")
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"
        ordering = ['order']


class City(models.Model):
    """
    Модель для городов.
    """
    name = models.CharField(max_length=50, db_index=True, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ['name']


class Favorite(models.Model):
    """
    Модель избранного объявления для пользователя.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='favorites', verbose_name='Пользователь')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='favorited_by', verbose_name='Объявление')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ('user', 'product')
        ordering = ['-created_at']


class ProductView(models.Model):
    """
    Модель для хранения просмотров объявлений.
    """
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='views', verbose_name='Объявление')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True, verbose_name='Пользователь')
    ip_address = models.GenericIPAddressField(verbose_name='IP адрес', blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True, verbose_name='Ключ сессии')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата просмотра')

    def __str__(self):
        if self.user:
            return f"{self.product.title} - {self.user.username}"
        return f"{self.product.title} - {self.ip_address}"

    class Meta:
        verbose_name = 'Просмотр объявления'
        verbose_name_plural = 'Просмотры объявлений'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'],
                condition=models.Q(user__isnull=False),
                name='unique_product_user_view'
            ),
            models.UniqueConstraint(
                fields=['product', 'ip_address', 'session_key'],
                condition=models.Q(user__isnull=True, ip_address__isnull=False, session_key__isnull=False),
                name='unique_product_ip_session_view'
            ),
        ]
        ordering = ['-created_at']



class BannerPost(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='Автор')
    title = models.CharField(max_length=50, verbose_name='Товар', db_index=True)
    link = models.URLField(max_length=200, verbose_name='Ссылка', blank=True, null=True)
    image = models.ImageField(upload_to='media/images/banner/', verbose_name='Изображение')