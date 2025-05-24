from django.urls import path
from .views import (
    ProductDetailView, CategoryDetailView,  ProductDeleteView,
    FavoriteListView, toggle_favorite, ProductListAPIView, CategoryProductsAPIView, change_product_status, FavoriteProductsAPIView,
    banner_ad_info, product_list, product_create, product_update, ProductListView,
    )   

app_name = 'app'

urlpatterns = [
    path('', ProductListView.as_view(), name='index'),
    path('product_list/', product_list, name='product_list'),
    path('product/create/', product_create, name='product_create'),
    path('product/<int:pk>/edit/', product_update, name='product_edit'),
    
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:pk>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', FavoriteListView.as_view(), name='favorites'),
    path('category/<slug:category_slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('product/<int:pk>/status/<int:status>/', change_product_status, name='change_status'),
    
    # API эндпоинты для бесконечной ленты
    path('api/products/', ProductListAPIView.as_view(), name='api_products'),
    path('api/category/<slug:category_slug>/products/', CategoryProductsAPIView.as_view(), name='api_category_products'),
    path('api/favorites/', FavoriteProductsAPIView.as_view(), name='api_favorites'),

    path('banner-ad-info/', banner_ad_info, name='banner_ad_info'),

]
