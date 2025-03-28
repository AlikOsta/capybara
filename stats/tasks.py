# stats/tasks.py
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta

from app.models import Product, ProductView, Favorite
from user_capybara.models import TelegramUser as User
from .models import DailyStats

def aggregate_daily_stats():
    """Агрегирует статистику за предыдущий день"""
    yesterday = timezone.now().date() - timedelta(days=1)
    
    # Проверяем, не агрегировали ли мы уже статистику за этот день
    if DailyStats.objects.filter(date=yesterday).exists():
        return
    
    # Считаем новых пользователей
    new_users = User.objects.filter(
        date_joined__date=yesterday
    ).count()
    
    # Считаем новые объявления
    new_products = Product.objects.filter(
        created_at__date=yesterday
    ).count()
    
    # Считаем просмотры
    product_views = ProductView.objects.filter(
        created_at__date=yesterday
    ).count()
    
    # Считаем добавления в избранное
    favorites_added = Favorite.objects.filter(
        created_at__date=yesterday
    ).count()
    
    # Сохраняем статистику
    DailyStats.objects.create(
        date=yesterday,
        new_users=new_users,
        new_products=new_products,
        product_views=product_views,
        favorites_added=favorites_added
    )
