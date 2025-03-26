from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import TelegramUser

class TelegramUserAdmin(UserAdmin):
    list_display = ('username', 'telegram_id', 'get_photo', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'telegram_id', 'first_name', 'last_name')
    readonly_fields = ('telegram_id', 'auth_date', 'get_photo_preview')
    
    fieldsets = (
        (None, {'fields': ('telegram_id', 'username', 'password')}),
        (_('Персональная информация'), {'fields': ('first_name', 'last_name', 'email', 'photo_url', 'get_photo_preview')}),
        (_('Telegram информация'), {'fields': ('auth_date',)}),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telegram_id', 'username', 'password1', 'password2'),
        }),
    )
    
    def get_photo(self, obj):
        if obj.photo_url:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%;" />', obj.photo_url)
        return "-"
    get_photo.short_description = 'Фото'
    
    def get_photo_preview(self, obj):
        if obj.photo_url:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 50%;" />', obj.photo_url)
        return "Нет фото"
    get_photo_preview.short_description = 'Предпросмотр фото'

admin.site.register(TelegramUser, TelegramUserAdmin)
