from .models import Favorite

def favorites_processor(request):
    """
    Добавляет список избранных объявлений в контекст всех шаблонов
    """
    if request.user.is_authenticated:
        favorite_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        return {'favorite_products': favorite_ids}
    return {'favorite_products': []}
