from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class TelegramUserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя Telegram"""
    
    def create_user(self, telegram_id, username=None, **extra_fields):
        """Создает и сохраняет пользователя с указанным telegram_id и username"""
        if not telegram_id:
            raise ValueError(_('Telegram ID обязателен'))
        
        user = self.model(
            telegram_id=telegram_id,
            username=username,
            **extra_fields
        )
        # Устанавливаем неиспользуемый пароль, т.к. авторизация через Telegram
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
    
    # Telegram-специфичные поля
    telegram_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID')
    first_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='Имя')
    last_name = models.CharField(max_length=64, blank=True, null=True, verbose_name='Фамилия')
    photo_url = models.URLField(blank=True, null=True, verbose_name='URL фото')
    auth_date = models.IntegerField(blank=True, null=True,verbose_name='Дата авторизации')
    
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
        """Возвращает полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        return f"User {self.telegram_id}"
    
    def get_short_name(self):
        """Возвращает короткое имя пользователя"""
        if self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        return f"User {self.telegram_id}"
