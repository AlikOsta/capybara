from datetime import timedelta
from django.utils import timezone
from .models import Product
from django_q.tasks import async_task
from .utils import moderate_goods
import logging

logger = logging.getLogger(__name__)


def archive_old_products():
    """
    Проверяет все активные объявления и переводит в архив те,
    которые не обновлялись более 1 дня
    """
    one_day_ago = timezone.now() - timedelta(days=28)
    
    old_products = Product.objects.filter(
        status=3, 
        updated_at__lt=one_day_ago 
    )
    
    count = old_products.update(status=4)
    
    return f"Архивировано {count} объявлений"


def moderate_product(product_id):
    print(f"Запущена задача для продукта с ID {product_id}")
    """
    Фоновая задача: проверяет контент продукта через ИИ и сохраняет результат.
    """
    try:
        product = Product.objects.get(pk=product_id)
        result = moderate_goods(product.description)
        if result:
            product.status = 3
        else:
            product.status = 2 
        product.save()
    except Product.DoesNotExist:
        logger.error(f"Ошибка при модерации продукта {product_id}: {str(e)}")
        pass