# stats/tasks.py
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from django_q.tasks import async_task, schedule
from django_q.models import Schedule

from app.models import Product, ProductView, Favorite
from user_capybara.models import TelegramUser
from .models import DailyStats

def aggregate_daily_stats():
    """
    Агрегирует статистику за предыдущий день.
    Эта функция вызывается ежедневно через Django Q.
    """
    yesterday = timezone.now().date() - timedelta(days=1)
    
    # Проверяем, не агрегировали ли мы уже статистику за этот день
    if DailyStats.objects.filter(date=yesterday).exists():
        return
    
    # Считаем новых пользователей
    new_users = TelegramUser.objects.filter(
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
    
    return {
        'date': yesterday.strftime('%Y-%m-%d'),
        'new_users': new_users,
        'new_products': new_products,
        'product_views': product_views,
        'favorites_added': favorites_added
    }

def update_current_day_stats():
    """
    Обновляет статистику за текущий день.
    Эта функция вызывается каждый час через Django Q.
    """
    today = timezone.now().date()
    
    # Получаем или создаем запись статистики за сегодня
    daily_stat, created = DailyStats.objects.get_or_create(date=today)
    
    # Получаем количество новых пользователей за сегодня
    new_users = TelegramUser.objects.filter(
        date_joined__date=today
    ).count()
    
    # Получаем количество новых объявлений за сегодня
    new_products = Product.objects.filter(
        created_at__date=today
    ).count()
    
    # Получаем количество просмотров за сегодня
    product_views = ProductView.objects.filter(
        created_at__date=today
    ).count()
    
    # Получаем количество добавлений в избранное за сегодня
    favorites_added = Favorite.objects.filter(
        created_at__date=today
    ).count()
    
    # Обновляем статистику
    daily_stat.new_users = new_users
    daily_stat.new_products = new_products
    daily_stat.product_views = product_views
    daily_stat.favorites_added = favorites_added
    daily_stat.save()
    
    return {
        'date': today.strftime('%Y-%m-%d'),
        'new_users': new_users,
        'new_products': new_products,
        'product_views': product_views,
        'favorites_added': favorites_added
    }

def schedule_stats_tasks():
    """
    Создает задачи для автоматического обновления статистики.
    Эта функция должна вызываться при запуске приложения.
    """
    # Удаляем существующие задачи с такими же именами
    Schedule.objects.filter(name__in=['aggregate_daily_stats', 'update_current_day_stats']).delete()
    
    # Создаем задачу для агрегации статистики за предыдущий день (каждый день в 00:05)
    schedule(
        'stats.tasks.aggregate_daily_stats',
        schedule_type=Schedule.DAILY,
        name='aggregate_daily_stats',
        next_run=timezone.now().replace(hour=0, minute=5, second=0) + timedelta(days=1)
    )
    
    # Создаем задачу для обновления статистики за текущий день (каждый час)
    schedule(
        'stats.tasks.update_current_day_stats',
        schedule_type=Schedule.HOURLY,
        name='update_current_day_stats',
        next_run=timezone.now().replace(minute=0, second=0) + timedelta(hours=1)
    )
    
    return True

def generate_monthly_report():
    """
    Генерирует ежемесячный отчет по статистике.
    Эта функция вызывается в первый день каждого месяца.
    """
    # Получаем первый и последний день предыдущего месяца
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    last_day_of_prev_month = first_day_of_month - timedelta(days=1)
    first_day_of_prev_month = last_day_of_prev_month.replace(day=1)
    
    # Получаем статистику за предыдущий месяц
    monthly_stats = DailyStats.objects.filter(
        date__gte=first_day_of_prev_month,
        date__lte=last_day_of_prev_month
    ).order_by('date')
    
    # Суммируем данные
    total_new_users = sum(stat.new_users for stat in monthly_stats)
    total_new_products = sum(stat.new_products for stat in monthly_stats)
    total_product_views = sum(stat.product_views for stat in monthly_stats)
    total_favorites_added = sum(stat.favorites_added for stat in monthly_stats)
    
    # Здесь можно добавить логику для отправки отчета по email или сохранения в файл
    
    return {
        'month': first_day_of_prev_month.strftime('%B %Y'),
        'total_new_users': total_new_users,
        'total_new_products': total_new_products,
        'total_product_views': total_product_views,
        'total_favorites_added': total_favorites_added
    }

def schedule_monthly_report():
    """
    Создает задачу для генерации ежемесячного отчета.
    """
    # Удаляем существующую задачу с таким же именем
    Schedule.objects.filter(name='generate_monthly_report').delete()
    
    # Создаем задачу для генерации отчета (первый день каждого месяца в 01:00)
    schedule(
        'stats.tasks.generate_monthly_report',
        schedule_type=Schedule.MONTHLY,
        name='generate_monthly_report',
        next_run=timezone.now().replace(day=1, hour=1, minute=0, second=0) + timedelta(days=32)
    )
    
    return True

def run_all_schedules():
    """
    Запускает все задачи по расписанию.
    Эта функция должна вызываться при запуске приложения.
    """
    schedule_stats_tasks()
    schedule_monthly_report()
    return True
