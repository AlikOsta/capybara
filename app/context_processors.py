
from django.core.cache import cache
from .models import Category, City, Currency, Favorite

def favorites_processor(request):
    """
    Добавляет список избранных объявлений в контекст всех шаблонов
    """
    if request.user.is_authenticated:
        favorite_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        return {'favorite_products': favorite_ids}
    return {'favorite_products': []}


def common_data(request):
    """
    Контекстный процессор для добавления общих данных в шаблоны.
    """
    # Кэшируем категории на 1 час
    categories = cache.get('all_categories')
    if categories is None:
        categories = Category.objects.all()
        cache.set('all_categories', categories, 60 * 60)
    
    # Кэшируем города на 1 час
    cities = cache.get('all_cities')
    if cities is None:
        cities = City.objects.all()
        cache.set('all_cities', cities, 60 * 60)
    
    # Кэшируем валюты на 1 час
    currencies = cache.get('all_currencies')
    if currencies is None:
        currencies = Currency.objects.all()
        cache.set('all_currencies', currencies, 60 * 60)
    
    return {
        'categories': categories,
        'cities': cities,
        'currencies': currencies,
    }
