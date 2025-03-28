from django.db import models

class DailyStats(models.Model):
    date = models.DateField(unique=True)
    new_users = models.IntegerField(default=0)
    new_products = models.IntegerField(default=0)
    product_views = models.IntegerField(default=0)
    favorites_added = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Cтатистика"
        verbose_name_plural = "Cтатистика"
        ordering = ['-date']
    
    def __str__(self):
        return f"Статистика за {self.date}"