from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg


class TelegramUserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя Telegram"""
    
    def create_user(self, telegram_id, username, password=None, **extra_fields):
        """
        Создаёт и сохраняет обычного пользователя с заданными telegram_id и username.
        """
        if not telegram_id:
            raise ValueError(_('The Telegram ID must be set'))
        
        user = self.model(telegram_id=telegram_id, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_id, username, password, **extra_fields):
        """
        Создаёт суперпользователя с заданными telegram_id, username и паролем.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError(_('Superuser must have is_staff=True.'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(telegram_id, username, password, **extra_fields)


class TelegramUser(AbstractUser):
    """Кастомная модель пользователя для авторизации через Telegram"""
    
    # Telegram-специфичные поля
    telegram_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    username = models.CharField(max_length=30, unique=True, verbose_name='Телеграм ник')
    first_name = models.CharField(max_length=64, blank=True, null=True,verbose_name='Ваше имя')
    last_name = models.CharField(max_length=64, blank=True, null=True,verbose_name='Ваша фамилия')
    photo_url = models.URLField(blank=True, null=True,verbose_name='URL фото')
    auth_date = models.IntegerField(blank=True, null=True,verbose_name='Дата авторизации')

    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = ['username']
    
    # Указываем кастомный менеджер
    objects = TelegramUserManager()
    
    class Meta:
        verbose_name = _('Пользователь Telegram')
        verbose_name_plural = _('Пользователи Telegram')
    
    def __str__(self):
        if self.username:
            return f"@{self.username}"
        return f"User {self.telegram_id}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_tg_name(self):
        return f"@{self.username}"