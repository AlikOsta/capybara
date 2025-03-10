from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import ProductListView, ProductDetailView, CategoryDetailView, ProductCreateView, AuthorProfileView

app_name = 'app'

urlpatterns = [
    path('', ProductListView.as_view(), name='index'),

    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<slug:product_slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:category_slug>/', CategoryDetailView.as_view(), name='category_detail'),
     path('author/<int:author_id>/', AuthorProfileView.as_view(), name='author_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
