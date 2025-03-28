# stats/views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render

from app.models import Product, ProductView, Favorite
from user_capybara.models import TelegramUser 

@staff_member_required
def user_stats_data(request):
    """API для получения статистики пользователей"""
    period = request.GET.get('period', 'month')
    
    # Определяем начальную дату в зависимости от периода
    if period == 'week':
        start_date = timezone.now() - timedelta(days=7)
        trunc_func = TruncDay
        date_format = '%d.%m'
    elif period == 'month':
        start_date = timezone.now() - timedelta(days=30)
        trunc_func = TruncDay
        date_format = '%d.%m'
    elif period == 'year':
        start_date = timezone.now() - timedelta(days=365)
        trunc_func = TruncMonth
        date_format = '%m.%Y'
    else:
        start_date = timezone.now() - timedelta(days=30)
        trunc_func = TruncDay
        date_format = '%d.%m'
    
    # Получаем статистику по новым пользователям
    users_stats = TelegramUser.objects.filter(  # Исправлено с User на TelegramUser
        date_joined__gte=start_date
    ).annotate(
        date=trunc_func('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Форматируем данные для графика
    labels = [item['date'].strftime(date_format) for item in users_stats]
    data = [item['count'] for item in users_stats]
    
    # Общая статистика
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    return JsonResponse({
        'labels': labels,
        'datasets': [{
            'label': 'Новые пользователи',
            'data': data,
            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 2,
        }],
        'total_users': total_users,
        'active_users': active_users,
    })

@staff_member_required
def product_stats_data(request):
    """API для получения статистики объявлений"""
    period = request.GET.get('period', 'month')
    
    # Определяем начальную дату в зависимости от периода
    if period == 'day':
        start_date = timezone.now() - timedelta(days=1)
        trunc_func = TruncDay
        date_format = '%H:00'
    elif period == 'week':
        start_date = timezone.now() - timedelta(days=7)
        trunc_func = TruncDay
        date_format = '%d.%m'
    elif period == 'month':
        start_date = timezone.now() - timedelta(days=30)
        trunc_func = TruncDay
        date_format = '%d.%m'
    elif period == 'year':
        start_date = timezone.now() - timedelta(days=365)
        trunc_func = TruncMonth
        date_format = '%m.%Y'
    else:
        start_date = timezone.now() - timedelta(days=30)
        trunc_func = TruncDay
        date_format = '%d.%m'
    
    # Получаем статистику по новым объявлениям
    products_stats = Product.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=trunc_func('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Форматируем данные для графика
    labels = [item['date'].strftime(date_format) for item in products_stats]
    data = [item['count'] for item in products_stats]
    
    # Статистика по статусам
    status_stats = Product.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    status_labels = ['На модерации', 'Одобрено', 'Отклонено', 'Опубликовано', 'Архив']
    status_data = [0, 0, 0, 0, 0]
    
    for item in status_stats:
        if 0 <= item['status'] <= 4:
            status_data[item['status']] = item['count']
    
    return JsonResponse({
        'labels': labels,
        'datasets': [{
            'label': 'Новые объявления',
            'data': data,
            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
            'borderColor': 'rgba(255, 99, 132, 1)',
            'borderWidth': 2,
        }],
        'status_labels': status_labels,
        'status_data': status_data,
        'total_products': Product.objects.count(),
        'active_products': Product.objects.filter(status=3).count(),
    })

@staff_member_required
def views_stats_data(request):
    """API для получения статистики просмотров и избранного"""
    period = request.GET.get('period', 'month')
    
    # Определяем начальную дату в зависимости от периода
    if period == 'day':
        start_date = timezone.now() - timedelta(days=1)
        trunc_func = TruncDay
        date_format = '%H:00'
    elif period == 'week':
        start_date = timezone.now() - timedelta(days=7)
        trunc_func = TruncDay
        date_format = '%d.%m'
    elif period == 'month':
        start_date = timezone.now() - timedelta(days=30)
        trunc_func = TruncDay
        date_format = '%d.%m'
    elif period == 'year':
        start_date = timezone.now() - timedelta(days=365)
        trunc_func = TruncMonth
        date_format = '%m.%Y'
    else:
        start_date = timezone.now() - timedelta(days=30)
        trunc_func = TruncDay
        date_format = '%d.%m'
    
    # Получаем статистику по просмотрам
    views_stats = ProductView.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=trunc_func('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Получаем статистику по избранному
    favorites_stats = Favorite.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=trunc_func('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Объединяем данные
    all_dates = set([item['date'] for item in views_stats] + [item['date'] for item in favorites_stats])
    all_dates = sorted(all_dates)
    
    labels = [date.strftime(date_format) for date in all_dates]
    
    views_data = [0] * len(labels)
    favorites_data = [0] * len(labels)
    
    for i, date in enumerate(all_dates):
        for item in views_stats:
            if item['date'] == date:
                views_data[i] = item['count']
                break
        
        for item in favorites_stats:
            if item['date'] == date:
                favorites_data[i] = item['count']
                break
    
    # Общая статистика
    total_views = ProductView.objects.count()
    total_favorites = Favorite.objects.count()
    
    return JsonResponse({
        'labels': labels,
        'datasets': [
            {
                'label': 'Просмотры',
                'data': views_data,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 2,
            },
            {
                'label': 'Добавлено в избранное',
                'data': favorites_data,
                'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                'borderColor': 'rgba(153, 102, 255, 1)',
                'borderWidth': 2,
            }
        ],
        'total_views': total_views,
        'total_favorites': total_favorites,
    })



@staff_member_required
def user_stats_view(request):
    """Страница статистики пользователей"""
    return render(request, 'admin/user_stats.html')

@staff_member_required
def product_stats_view(request):
    """Страница статистики объявлений"""
    return render(request, 'admin/product_stats.html')

@staff_member_required
def views_stats_view(request):
    """Страница статистики просмотров и избранного"""
    return render(request, 'admin/views_stats.html')