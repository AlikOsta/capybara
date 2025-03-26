from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Currency, City

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price_with_currency', 'city', 'status_badge', 'author', 'created_at', 'view_count')
    list_filter = ('status', 'category', 'city', 'currency', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    readonly_fields = ('created_at', 'updated_at', 'get_image_preview')
    date_hierarchy = 'created_at'
    list_per_page = 20
    actions = ['approve_products', 'publish_products', 'reject_products', 'archive_products']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'author')
        }),
        ('Изображение', {
            'fields': ('image', 'get_image_preview')
        }),
        ('Цена и местоположение', {
            'fields': ('price', 'currency', 'city')
        }),
        ('Статус и даты', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" height="auto" />', obj.image.url)
        return "Нет изображения"
    get_image_preview.short_description = 'Предпросмотр изображения'
    
    def price_with_currency(self, obj):
        return f"{obj.price} {obj.currency}"
    price_with_currency.short_description = 'Цена'
    
    def status_badge(self, obj):
        status_colors = {
            0: 'warning',  # На модерации
            1: 'info',     # Одобрено
            2: 'danger',   # Отклонено
            3: 'success',  # Опубликовано
            4: 'secondary' # Архив
        }
        status_names = {
            0: 'На модерации',
            1: 'Одобрено',
            2: 'Отклонено',
            3: 'Опубликовано',
            4: 'В архиве'
        }
        color = status_colors.get(obj.status, 'primary')
        name = status_names.get(obj.status, 'Неизвестно')
        return format_html('<span style="background-color: {}; color: white; padding: 3px 7px; border-radius: 3px;">{}</span>', 
                          {'warning': '#ffc107', 'info': '#17a2b8', 'danger': '#dc3545', 
                           'success': '#28a745', 'secondary': '#6c757d', 'primary': '#007bff'}[color], 
                          name)
    status_badge.short_description = 'Статус'
    
    def view_count(self, obj):
        return obj.get_view_count()
    view_count.short_description = 'Просмотры'
    
    # Массовые действия
    def approve_products(self, request, queryset):
        """Одобрить выбранные объявления (статус 1)"""
        updated = queryset.update(status=1)
        self.message_user(request, f'Одобрено {updated} объявлений.')
    approve_products.short_description = "Одобрить выбранные объявления"
    
    def publish_products(self, request, queryset):
        """Опубликовать выбранные объявления (статус 3)"""
        updated = queryset.update(status=3)
        self.message_user(request, f'Опубликовано {updated} объявлений.')
    publish_products.short_description = "Опубликовать выбранные объявления"
    
    def reject_products(self, request, queryset):
        """Отклонить выбранные объявления (статус 2)"""
        updated = queryset.update(status=2)
        self.message_user(request, f'Отклонено {updated} объявлений.')
    reject_products.short_description = "Отклонить выбранные объявления"
    
    def archive_products(self, request, queryset):
        """Архивировать выбранные объявления (статус 4)"""
        updated = queryset.update(status=4)
        self.message_user(request, f'Архивировано {updated} объявлений.')
    archive_products.short_description = "Архивировать выбранные объявления"

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'get_image_preview')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="auto" />', obj.image.url)
        return "Нет изображения"
    get_image_preview.short_description = 'Изображение'

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'code')

class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ProductViewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__title', 'user__username', 'ip_address')
    date_hierarchy = 'created_at'
    readonly_fields = ('product', 'user', 'ip_address', 'session_key', 'created_at')

# Регистрация моделей с кастомными админ-классами
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(City, CityAdmin)

