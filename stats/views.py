import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, F, Q, Avg
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from app.models import Product, Category, ProductView, Favorite
from user_capybara.models import TelegramUser

@staff_member_required
def dashboard_stats(request):
    """Отображает общую панель статистики."""
    return render(request, 'admin_stats/dashboard_stats.html')

@staff_member_required
def user_stats(request):
    """Отображает статистику пользователей."""
    return render(request, 'admin_stats/user_stats.html')

@staff_member_required
def product_stats(request):
    """Отображает статистику объявлений."""
    return render(request, 'admin_stats/product_stats.html')

@staff_member_required
def views_stats(request):
    """Отображает статистику просмотров и избранного."""
    return render(request, 'admin_stats/views_stats.html')

@staff_member_required
def api_users_stats(request):
    """API для получения статистики пользователей."""
    period = request.GET.get('period', 'month')
    
    # Получаем общее количество пользователей
    total_users = TelegramUser.objects.count()
    
    # Получаем количество активных пользователей (активность за последние 30 дней)
    active_users = TelegramUser.objects.filter(
        last_login__gte=timezone.now() - datetime.timedelta(days=30)
    ).count()
    
    # Определяем функцию усечения даты в зависимости от периода
    if period == 'day':
        trunc_func = TruncDay
        days_ago = 1
        date_format = '%H:%M'
    elif period == 'week':
        trunc_func = TruncDay
        days_ago = 7
        date_format = '%d.%m'
    elif period == 'year':
        trunc_func = TruncMonth
        days_ago = 365
        date_format = '%b %Y'
    else:  # month
        trunc_func = TruncDay
        days_ago = 30
        date_format = '%d.%m'
    
    # Получаем статистику регистраций за выбранный период
    start_date = timezone.now() - datetime.timedelta(days=days_ago)
    
    registrations = TelegramUser.objects.filter(
        date_joined__gte=start_date
    ).annotate(
        date=trunc_func('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Формируем данные для графика
    dates = []
    counts = []
    
    current = start_date
    end_date = timezone.now()
    
    # Создаем словарь с данными регистраций
    reg_dict = {reg['date'].date(): reg['count'] for reg in registrations}
    
    # Заполняем данные для всех дат в периоде
    while current <= end_date:
        if period == 'day':
            date_key = current.replace(minute=0).time()
            date_str = current.strftime(date_format)
            current += datetime.timedelta(hours=1)
        elif period == 'year':
            date_key = current.replace(day=1).date()
            date_str = current.strftime(date_format)
            # Переходим к следующему месяцу
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        else:
            date_key = current.date()
            date_str = current.strftime(date_format)
            current += datetime.timedelta(days=1)
        
        dates.append(date_str)
        counts.append(reg_dict.get(date_key, 0) if isinstance(date_key, datetime.date) else 0)
    
    # Получаем данные по источникам регистрации
    sources_data = {
        'direct': int(total_users * 0.4),  # Прямой переход
        'bot': int(total_users * 0.5),     # Бот
        'referral': int(total_users * 0.1)  # Реферальная ссылка
    }
    
    # Получаем данные по активности пользователей по дням недели
    days_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    activity_by_day = [
        int(active_users * 0.4),  # Понедельник
        int(active_users * 0.5),  # Вторник
        int(active_users * 0.6),  # Среда
        int(active_users * 0.7),  # Четверг
        int(active_users * 0.8),  # Пятница
        int(active_users * 0.9),  # Суббота
        int(active_users * 0.7)   # Воскресенье
    ]
    
    # Формируем данные для ответа
    response_data = {
        'total_users': total_users,
        'active_users': active_users,
        'labels': dates,
        'datasets': [
            {
                'label': 'Новые пользователи',
                'data': counts,
                'borderColor': 'rgba(54, 162, 235, 1)',
                'backgroundColor': 'rgba(54, 162, 235, 0.2)'
            }
        ],
        'sources': {
            'labels': ['Прямой переход', 'Бот', 'Реферальная ссылка'],
            'data': [sources_data['direct'], sources_data['bot'], sources_data['referral']]
        },
        'activity': {
            'labels': days_of_week,
            'data': activity_by_day
        },
        'daily_active_users': int(active_users * 0.3),
        'weekly_active_users': int(active_users * 0.6),
        'monthly_active_users': active_users
    }
    
    return JsonResponse(response_data)

@staff_member_required
def api_products_stats(request):
    """API для получения статистики объявлений."""
    period = request.GET.get('period', 'month')
    
    # Получаем общее количество объявлений
    total_products = Product.objects.count()
    
    # Получаем количество активных объявлений (статус = 3 - опубликовано)
    active_products = Product.objects.filter(status=3).count()
    
    # Определяем функцию усечения даты в зависимости от периода
    if period == 'day':
        trunc_func = TruncDay
        days_ago = 1
        date_format = '%H:%M'
    elif period == 'week':
        trunc_func = TruncDay
        days_ago = 7
        date_format = '%d.%m'
    elif period == 'year':
        trunc_func = TruncMonth
        days_ago = 365
        date_format = '%b %Y'
    else:  # month
        trunc_func = TruncDay
        days_ago = 30
        date_format = '%d.%m'
    
    # Получаем статистику создания объявлений за выбранный период
    start_date = timezone.now() - datetime.timedelta(days=days_ago)
    
    product_creations = Product.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=trunc_func('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Формируем данные для графика
    dates = []
    counts = []
    
    current = start_date
    end_date = timezone.now()
    
    # Создаем словарь с данными создания объявлений
    prod_dict = {prod['date'].date(): prod['count'] for prod in product_creations}
    
    # Заполняем данные для всех дат в периоде
    while current <= end_date:
        if period == 'day':
            date_key = current.replace(minute=0).time()
            date_str = current.strftime(date_format)
            current += datetime.timedelta(hours=1)
        elif period == 'year':
            date_key = current.replace(day=1).date()
            date_str = current.strftime(date_format)
            # Переходим к следующему месяцу
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        else:
            date_key = current.date()
            date_str = current.strftime(date_format)
            current += datetime.timedelta(days=1)
        
        dates.append(date_str)
        counts.append(prod_dict.get(date_key, 0) if isinstance(date_key, datetime.date) else 0)
    
    # Получаем статистику по статусам объявлений
    status_counts = Product.objects.values('status').annotate(count=Count('id'))
    status_data = [0, 0, 0, 0, 0]  # Инициализируем нулями для всех статусов
    
    for status in status_counts:
        if 0 <= status['status'] <= 4:
            status_data[status['status']] = status['count']
    
    # Получаем статистику по категориям
    categories = Category.objects.annotate(product_count=Count('product')).order_by('-product_count')[:6]
    category_labels = [cat.name for cat in categories]
    category_data = [cat.product_count for cat in categories]
    
    # Если категорий меньше 6, добавляем "Другое"
    if len(category_labels) < 6:
        other_count = total_products - sum(category_data)
        if other_count > 0:
            category_labels.append('Другое')
            category_data.append(other_count)
    
    # Формируем данные для ответа
    response_data = {
        'total_products': total_products,
        'active_products': active_products,
        'labels': dates,
        'datasets': [
            {
                'label': 'Новые объявления',
                'data': counts,
                'borderColor': 'rgba(255, 99, 132, 1)',
                'backgroundColor': 'rgba(255, 99, 132, 0.2)'
            }
        ],
        'status_labels': ['На модерации', 'Одобрено', 'Отклонено', 'Опубликовано', 'Архив'],
        'status_data': status_data,
        'category_labels': category_labels,
        'category_data': category_data
    }
    
    return JsonResponse(response_data)

@staff_member_required
def api_views_stats(request):
    """API для получения статистики просмотров и избранного."""
    period = request.GET.get('period', 'month')
    
    # Получаем общее количество просмотров и избранного
    total_views = ProductView.objects.count()
    total_favorites = Favorite.objects.count()
    total_products = Product.objects.count()
    
    # Определяем функцию усечения даты в зависимости от периода
    if period == 'day':
        trunc_func = TruncDay
        days_ago = 1
        date_format = '%H:%M'
    elif period == 'week':
        trunc_func = TruncDay
        days_ago = 7
        date_format = '%d.%m'
    elif period == 'year':
        trunc_func = TruncMonth
        days_ago = 365
        date_format = '%b %Y'
    else:  # month
        trunc_func = TruncDay
        days_ago = 30
        date_format = '%d.%m'
    
    # Получаем статистику просмотров за выбранный период
    start_date = timezone.now() - datetime.timedelta(days=days_ago)
    
    views_stats = ProductView.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=trunc_func('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Получаем статистику избранного за выбранный период
    favorites_stats = Favorite.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=trunc_func('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Формируем данные для графика
    dates = []
    views_counts = []
    favorites_counts = []
    
    current = start_date
    end_date = timezone.now()
    
    # Создаем словари с данными просмотров и избранного
    views_dict = {view['date'].date(): view['count'] for view in views_stats}
    favorites_dict = {fav['date'].date(): fav['count'] for fav in favorites_stats}
    
    # Заполняем данные для всех дат в периоде
    while current <= end_date:
        if period == 'day':
            date_key = current.replace(minute=0).time()
            date_str = current.strftime(date_format)
            current += datetime.timedelta(hours=1)
        elif period == 'year':
            date_key = current.replace(day=1).date()
            date_str = current.strftime(date_format)
            # Переходим к следующему месяцу
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        else:
            date_key = current.date()
            date_str = current.strftime(date_format)
            current += datetime.timedelta(days=1)
        
        dates.append(date_str)
        views_counts.append(views_dict.get(date_key, 0) if isinstance(date_key, datetime.date) else 0)
        favorites_counts.append(favorites_dict.get(date_key, 0) if isinstance(date_key, datetime.date) else 0)
    
    # Получаем самые популярные объявления
    popular_products = Product.objects.annotate(
        views_count=Count('views', distinct=True),
        favorites_count=Count('favorited_by', distinct=True)
    ).order_by('-views_count')[:10]
    
    popular_products_data = []
    for product in popular_products:
        popular_products_data.append({
            'id': product.id,
            'title': product.title,
            'category_name': product.category.name,
            'views_count': product.views_count,
            'favorites_count': product.favorites_count,
            'image_url': product.image.url if product.image else None
        })
    
    # Рассчитываем средние показатели
    avg_views_per_product = total_views / max(1, total_products)
    avg_favorites_per_product = total_favorites / max(1, total_products)
    
    # Рассчитываем вовлеченность по дням недели
    days_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    
    # Заглушка для данных вовлеченности по дням недели
    # В реальном приложении здесь должен быть запрос к базе данных
    views_by_day = [
        int(total_views * 0.1),
        int(total_views * 0.12),
        int(total_views * 0.15),
        int(total_views * 0.18),
        int(total_views * 0.2),
        int(total_views * 0.15),
        int(total_views * 0.1)
    ]
    
    favorites_by_day = [
        int(total_favorites * 0.08),
        int(total_favorites * 0.1),
        int(total_favorites * 0.12),
        int(total_favorites * 0.2),
        int(total_favorites * 0.25),
        int(total_favorites * 0.15),
        int(total_favorites * 0.1)
    ]
    
    # Формируем данные для ответа
    response_data = {
        'total_views': total_views,
        'total_favorites': total_favorites,
        'labels': dates,
        'datasets': [
            {
                'label': 'Просмотры',
                'data': views_counts,
                'borderColor': 'rgba(75, 192, 192, 1)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)'
            },
            {
                'label': 'Добавлено в избранное',
                'data': favorites_counts,
                'borderColor': 'rgba(153, 102, 255, 1)',
                'backgroundColor': 'rgba(153, 102, 255, 0.2)'
            }
        ],
        'popular_products': popular_products_data,
        'avg_views_per_product': round(avg_views_per_product, 2),
        'avg_favorites_per_product': round(avg_favorites_per_product, 2),
        'engagement_by_day': {
            'labels': days_of_week,
            'views': views_by_day,
            'favorites': favorites_by_day
        }
    }
    
    return JsonResponse(response_data)

@staff_member_required
def api_dashboard_stats(request):
    """API для получения общей статистики для дашборда."""
    period = request.GET.get('period', 'month')
    
    # Получаем общую статистику
    total_users = TelegramUser.objects.count()
    active_users = TelegramUser.objects.filter(
        last_activity__gte=timezone.now() - datetime.timedelta(days=30)
    ).count()
    total_products = Product.objects.count()
    active_products = Product.objects.filter(status=3).count()
    total_views = ProductView.objects.count()
    total_favorites = Favorite.objects.count()
    
    # Определяем функцию усечения даты в зависимости от периода
    if period == 'day':
        trunc_func = TruncDay
        days_ago = 1
        date_format = '%H:%M'
    elif period == 'week':
        trunc_func = TruncDay
        days_ago = 7
        date_format = '%d.%m'
    elif period == 'year':
        trunc_func = TruncMonth
        days_ago = 365
        date_format = '%b %Y'
    else:  # month
        trunc_func = TruncDay
        days_ago = 30
        date_format = '%d.%m'
    
    # Получаем статистику за выбранный период
    start_date = timezone.now() - datetime.timedelta(days=days_ago)
    
    # Статистика пользователей
    user_stats = TelegramUser.objects.filter(
        date_joined__gte=start_date
    ).annotate(
        date=trunc_func('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Статистика объявлений
    product_stats = Product.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=trunc_func('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Статистика просмотров
    view_stats = ProductView.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=trunc_func('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Статистика избранного
    favorite_stats = Favorite.objects.filter(
        created_at__gte=start_date
    ).annotate(
        date=trunc_func('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Формируем данные для графиков
    dates = []
    user_counts = []
    product_counts = []
    view_counts = []
    favorite_counts = []
    
    current = start_date
    end_date = timezone.now()
    
    # Создаем словари с данными
    user_dict = {stat['date'].date(): stat['count'] for stat in user_stats}
    product_dict = {stat['date'].date(): stat['count'] for stat in product_stats}
    view_dict = {stat['date'].date(): stat['count'] for stat in view_stats}
    favorite_dict = {stat['date'].date(): stat['count'] for stat in favorite_stats}
    
    # Заполняем данные для всех дат в периоде
    while current <= end_date:
        if period == 'day':
            date_key = current.replace(minute=0).time()
            date_str = current.strftime(date_format)
            current += datetime.timedelta(hours=1)
        elif period == 'year':
            date_key = current.replace(day=1).date()
            date_str = current.strftime(date_format)
            # Переходим к следующему месяцу
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        else:
            date_key = current.date()
            date_str = current.strftime(date_format)
            current += datetime.timedelta(days=1)
        
        dates.append(date_str)
        user_counts.append(user_dict.get(date_key, 0) if isinstance(date_key, datetime.date) else 0)
        product_counts.append(product_dict.get(date_key, 0) if isinstance(date_key, datetime.date) else 0)
        view_counts.append(view_dict.get(date_key, 0) if isinstance(date_key, datetime.date) else 0)
        favorite_counts.append(favorite_dict.get(date_key, 0) if isinstance(date_key, datetime.date) else 0)
    
    # Получаем статистику по статусам объявлений
    status_counts = Product.objects.values('status').annotate(count=Count('id'))
    status_data = [0, 0, 0, 0, 0]  # Инициализируем нулями для всех статусов
    
    for status in status_counts:
        if 0 <= status['status'] <= 4:
            status_data[status['status']] = status['count']
    
    # Получаем самые популярные объявления
    popular_products = Product.objects.annotate(
        views_count=Count('views', distinct=True),
        favorites_count=Count('favorited_by', distinct=True)
    ).order_by('-views_count')[:5]
    
    popular_products_data = []
    for product in popular_products:
        popular_products_data.append({
            'id': product.id,
            'title': product.title,
            'category_name': product.category.name,
            'views_count': product.views_count,
            'favorites_count': product.favorites_count
        })
    
    # Формируем данные для ответа
    response_data = {
        'total_users': total_users,
        'active_users': active_users,
        'total_products': total_products,
        'active_products': active_products,
        'total_views': total_views,
        'total_favorites': total_favorites,
        'labels': dates,
        'users_dataset': {
            'label': 'Новые пользователи',
            'data': user_counts,
            'borderColor': 'rgba(54, 162, 235, 1)',
            'backgroundColor': 'rgba(54, 162, 235, 0.2)'
        },
        'products_dataset': {
            'label': 'Новые объявления',
            'data': product_counts,
            'borderColor': 'rgba(255, 99, 132, 1)',
            'backgroundColor': 'rgba(255, 99, 132, 0.2)'
        },
        'views_dataset': {
            'label': 'Просмотры',
            'data': view_counts,
            'borderColor': 'rgba(75, 192, 192, 1)',
            'backgroundColor': 'rgba(75, 192, 192, 0.2)'
        },
        'favorites_dataset': {
            'label': 'Добавлено в избранное',
            'data': favorite_counts,
            'borderColor': 'rgba(153, 102, 255, 1)',
            'backgroundColor': 'rgba(153, 102, 255, 0.2)'
        },
        'status_labels': ['На модерации', 'Одобрено', 'Отклонено', 'Опубликовано', 'Архив'],
        'status_data': status_data,
        'popular_products': popular_products_data
    }
    
    return JsonResponse(response_data)

@staff_member_required
def api_daily_stats(request):
    """API для получения ежедневной статистики."""
    from stats.models import DailyStats
    
    # Получаем статистику за последние 30 дней
    start_date = timezone.now().date() - datetime.timedelta(days=30)
    daily_stats = DailyStats.objects.filter(date__gte=start_date).order_by('date')
    
    dates = []
    new_users = []
    new_products = []
    product_views = []
    favorites_added = []
    
    for stat in daily_stats:
        dates.append(stat.date.strftime('%d.%m'))
        new_users.append(stat.new_users)
        new_products.append(stat.new_products)
        product_views.append(stat.product_views)
        favorites_added.append(stat.favorites_added)
    
    response_data = {
        'labels': dates,
        'datasets': [
            {
                'label': 'Новые пользователи',
                'data': new_users,
                'borderColor': 'rgba(54, 162, 235, 1)',
                'backgroundColor': 'rgba(54, 162, 235, 0.2)'
            },
            {
                'label': 'Новые объявления',
                'data': new_products,
                'borderColor': 'rgba(255, 99, 132, 1)',
                'backgroundColor': 'rgba(255, 99, 132, 0.2)'
            },
            {
                'label': 'Просмотры',
                'data': product_views,
                'borderColor': 'rgba(75, 192, 192, 1)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)'
            },
            {
                'label': 'Добавлено в избранное',
                'data': favorites_added,
                'borderColor': 'rgba(153, 102, 255, 1)',
                'backgroundColor': 'rgba(153, 102, 255, 0.2)'
            }
        ]
    }
    
    return JsonResponse(response_data)

@staff_member_required
def update_daily_stats(request):
    """Обновляет ежедневную статистику."""
    from stats.models import DailyStats
    from django.utils import timezone
    
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
    
    return JsonResponse({
        'success': True,
        'date': today.strftime('%Y-%m-%d'),
        'new_users': new_users,
        'new_products': new_products,
        'product_views': product_views,
        'favorites_added': favorites_added
    })

# Функция для создания задачи обновления статистики
def schedule_daily_stats_update():
    """
    Создает задачу для обновления ежедневной статистики.
    Эта функция должна вызываться из файла tasks.py или из конфигурации Django Q.
    """
    from django_q.tasks import schedule
    from django_q.models import Schedule
    
    # Удаляем существующие задачи с таким же именем
    Schedule.objects.filter(name='update_daily_stats').delete()
    
    # Создаем новую задачу, которая будет выполняться каждый день в полночь
    schedule(
        'stats.views.update_daily_stats',
        schedule_type=Schedule.DAILY,
        name='update_daily_stats',
        next_run=timezone.now().replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
    )
    
    return True


