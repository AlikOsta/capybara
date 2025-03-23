from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import ProductListView, ProductDetailView, CategoryDetailView, ProductCreateView, ProductDeleteView, ProductUpdateView

app_name = 'app'

urlpatterns = [
    path('', ProductListView.as_view(), name='index'),

    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('category/<slug:category_slug>/', CategoryDetailView.as_view(), name='category_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
