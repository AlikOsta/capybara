from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import ProductListView, ProductDetailView

app_name = 'app'

urlpatterns = [
    path('', ProductListView.as_view(), name='index'),
    path('product/<slug:product_slug>/', ProductDetailView.as_view(), name='product_detail'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)