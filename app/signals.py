
from django.db.models.signals import m2m_changed, pre_save, post_save
from django.dispatch import receiver
from .models import Product
from .utils import moderate_goods


@receiver(post_save, sender=Product)
def product_post_save(sender, instance, created, **kwargs):
    # Проверяем, что это новое объявление или объявление на модерации
    if created or instance.status == 0:
        goods_text = f"{instance.title}\n{instance.description}"
        
        # Запускаем модерацию
        if moderate_goods(goods_text):
            instance.status = 1  # Одобрено
        else:
            instance.status = 2  # Отклонено
            
        # Важно: используем update для предотвращения рекурсивного вызова сигнала
        type(instance).objects.filter(pk=instance.pk).update(status=instance.status)