from django.contrib import admin
from .models import Product, Category, Currency, City, Favorite

# пстая регистрация модели 
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Currency)
admin.site.register(City)
admin.site.register(Favorite)


