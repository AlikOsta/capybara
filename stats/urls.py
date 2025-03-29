from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    # Страницы статистики
    path('dashboard/', views.dashboard_stats, name='dashboard_stats'),
    path('user_stats/', views.user_stats, name='user_stats'),
    path('product_stats/', views.product_stats, name='product_stats'),
    path('views_stats/', views.views_stats, name='views_stats'),
    
    # API для получения данных
    path('api/users/', views.api_users_stats, name='api_users_stats'),
    path('api/products/', views.api_products_stats, name='api_products_stats'),
    path('api/views/', views.api_views_stats, name='api_views_stats'),
    path('api/dashboard/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/daily/', views.api_daily_stats, name='api_daily_stats'),
    
    # Обновление ежедневной статистики
    path('update_daily_stats/', views.update_daily_stats, name='update_daily_stats'),
]
