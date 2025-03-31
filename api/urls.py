from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .views import (
    ProductViewSet, CategoryViewSet, CurrencyViewSet, 
    CityViewSet, FavoriteViewSet, UserViewSet
)

# Схема API для Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Capybara API",
        default_version='v1',
        description="API для маркетплейса Capybara",
        terms_of_service="https://www.capybarashop.store/terms/",
        contact=openapi.Contact(email="contact@capybarashop.store"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'currencies', CurrencyViewSet)
router.register(r'cities', CityViewSet)
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Документация API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]