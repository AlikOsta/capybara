from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import TelegramUser

@admin.register(TelegramUser)
class TelegramUserAdmin(UserAdmin):
    """Админка для кастомной модели пользователя Telegram"""
    
    list_display = ('telegram_id', 'username', 'first_name_tg', 'last_name_tg', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('telegram_id', 'username', 'first_name_tg', 'last_name_tg')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('telegram_id', 'username')}),
        (_('Персональная информация'), {'fields': ('first_name_tg', 'last_name_tg', 'phone_number', 'photo_url', 'photo', 'bio')}),
        (_('Права доступа'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Важные даты'), {'fields': ('last_login', 'last_login_telegram', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telegram_id', 'username', 'is_staff', 'is_active'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
