from django.urls import path
from .views import (
    ProductDetailView,  ProductDeleteView,
    FavoriteListView, toggle_favorite, change_product_status, FavoriteProductsAPIView,
    banner_ad_info, product_list, ProductUpdateView, ProductCreateView, index, category_detail, category_product_list
    )   

app_name = 'app'

urlpatterns = [
    path('', index, name='index'),
    path('product_list/', product_list, name='product_list'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),

    path('category/<slug:category_slug>/', category_detail, name='category_detail'),
    path('category/<slug:category_slug>/products/', category_product_list, name='category_product_list'),


    
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    path('favorites/', FavoriteListView.as_view(), name='favorites'),

    path('product/<int:pk>/status/<int:status>/', change_product_status, name='change_status'),
    
    path('api/favorites/', FavoriteProductsAPIView.as_view(), name='api_favorites'),
    path('product/<int:pk>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('banner-ad-info/', banner_ad_info, name='banner_ad_info'),

]
