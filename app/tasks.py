from datetime import timedelta
from django.utils import timezone
from .models import Product

def archive_old_products():
    """
    Проверяет все активные объявления и переводит в архив те,
    которые не обновлялись более 1 дня
    """
    # Получаем время, которое было 1 день назад
    one_day_ago = timezone.now() - timedelta(days=1)
    
    # Находим все объявления со статусом "Опубликовано" (3), 
    # которые не обновлялись более 1 дня
    old_products = Product.objects.filter(
        status=3,  # Опубликовано
        updated_at__lt=one_day_ago  # Обновлено более 1 дня назад
    )
    
    # Обновляем статус на "Архив" (4)
    count = old_products.update(status=4)
    
    return f"Архивировано {count} объявлений"
