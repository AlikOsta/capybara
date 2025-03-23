from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class TelegramUserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя Telegram"""
    
    def create_user(self, telegram_id, username=None, password=None, **extra_fields):
        """Создает и сохраняет пользователя с указанным telegram_id и username"""
        if not telegram_id:
            raise ValueError(_('Telegram ID обязателен'))
        
        user = self.model(
            telegram_id=telegram_id,
            username=username,
            **extra_fields
        )
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, telegram_id, username=None, **extra_fields):
        """Создает и сохраняет суперпользователя с указанным telegram_id и username"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))
        
        return self.create_user(telegram_id, username, **extra_fields)
    

class TelegramUser(AbstractUser):
    """Кастомная модель пользователя для авторизации через Telegram"""
    
    # Отключаем стандартные поля, которые нам не нужны
    first_name = None
    last_name = None
    email = None
    
    # Telegram-специфичные поля
    telegram_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    username = models.CharField(max_length=32, blank=True, null=True, verbose_name= 'Имя пользователя') # Имя пользователя в Telegram (без @)
    first_name_tg = models.CharField(max_length=64, blank=True, null=True, verbose_name='Имя') # Имя пользователя из Telegram
    last_name_tg = models.CharField(max_length=64, blank=True, null=True, verbose_name='Фамилия') # Фамилия пользователя из Telegram
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Номер телефона') # Номер телефона пользователя 
    photo_url = models.URLField(blank=True, null=True,verbose_name='URL фото') # URL фото пользователя из Telegram
    photo = models.ImageField(upload_to='telegram_users/', blank=True, null=True, verbose_name='Фото') # Фото пользователя
    bio = models.TextField(blank=True, null=True, verbose_name='О себе') # Описание пользователя 
    last_login_telegram = models.DateTimeField(blank=True, null=True, verbose_name='Последний вход через Telegram') # Дополнительные поля для статистики
    
    # Указываем кастомный менеджер
    objects = TelegramUserManager()
    
    # Указываем поле для использования в качестве имени пользователя
    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('Пользователь Telegram')
        verbose_name_plural = _('Пользователи Telegram')
    
    def __str__(self):
        if self.username:
            return f"@{self.username}"
        return f"User {self.telegram_id}"
    
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        if self.first_name_tg and self.last_name_tg:
            return f"{self.first_name_tg} {self.last_name_tg}"
        elif self.first_name_tg:
            return self.first_name_tg
        elif self.username:
            return f"@{self.username}"
        return f"User {self.telegram_id}"
    
    def get_short_name(self):
        """Возвращает короткое имя пользователя"""
        if self.first_name_tg:
            return self.first_name_tg
        elif self.username:
            return f"@{self.username}"
        return f"User {self.telegram_id}"
    
    def save(self, *args, **kwargs):
        # Если это новый пользователь и username не указан, используем telegram_id
        if not self.pk and not self.username:
            self.username = f"user_{self.telegram_id}"
        super().save(*args, **kwargs)
