import django_filters
from app.models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category_slug = django_filters.CharFilter(field_name='category__slug')
    
    class Meta:
        model = Product
        fields = ['category', 'city', 'currency', 'status', 'min_price', 'max_price', 'category_slug']
