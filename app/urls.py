from django.urls import path
from .views import (
    ProductListView, ProductDetailView, CategoryDetailView, 
    ProductCreateView, ProductUpdateView, ProductDeleteView,
    FavoriteListView, toggle_favorite, ProductListAPIView, CategoryProductsAPIView
)

app_name = 'app'

urlpatterns = [
    path('', ProductListView.as_view(), name='index'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:pk>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', FavoriteListView.as_view(), name='favorites'),
    path('category/<slug:category_slug>/', CategoryDetailView.as_view(), name='category_detail'),
    
    # API эндпоинты для бесконечной ленты
    path('api/products/', ProductListAPIView.as_view(), name='api_products'),
    path('api/category/<slug:category_slug>/products/', CategoryProductsAPIView.as_view(), name='api_category_products'),
]
