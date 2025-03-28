# stats/urls.py
from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    # API для получения данных
    path('api/users/', views.user_stats_data, name='user_stats_data'),
    path('api/products/', views.product_stats_data, name='product_stats_data'),
    path('api/views/', views.views_stats_data, name='views_stats_data'),
    
    # Страницы статистики
    path('user_stats/', views.user_stats_view, name='user_stats'),
    path('product_stats/', views.product_stats_view, name='product_stats'),
    path('views_stats/', views.views_stats_view, name='views_stats'),
]


