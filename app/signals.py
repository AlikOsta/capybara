
from django.db.models.signals import m2m_changed, pre_save, post_save
from django.dispatch import receiver
from .models import Product
from .utils import moderate_review


@receiver(post_save, sender=Product)
def review_post_save(sender, instance, created, **kwargs):
    if created:
        review = instance
        review_text = f"{instance.title}\n{instance.description}"
        
        if moderate_review(review_text):
            review.status = 1  
        else:
            review.status = 2  
            
        review.save()