from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from user_capybara.models import TelegramUser
from django.contrib.auth import get_user_model

from app.models import Product, Category, Currency, City, Favorite, ProductView
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    CategorySerializer, CurrencySerializer, CitySerializer, FavoriteSerializer, UserSerializer, UserUpdateSerializer
)
from .permissions import IsAuthorOrReadOnly
from .filters import ProductFilter

User = get_user_model()

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('author', 'category', 'currency', 'city')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter  # Используем кастомный фильтр
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'price']
    ordering = ['-created_at']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по статусу для обычных пользователей
        user = self.request.user
        if not user.is_staff and not user.is_superuser:
            if user.is_authenticated:
                # Авторизованные пользователи могут видеть свои объявления с любым статусом
                # и опубликованные объявления других пользователей
                queryset = queryset.filter(
                    Q(status=3) | Q(author=user)
                )
            else:
                # Неавторизованные пользователи видят только опубликованные объявления
                queryset = queryset.filter(status=3)
        
        # Поиск
        query = self.request.query_params.get('q', None)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user, status=0)  # Статус "На модерации"
    
    def perform_update(self, serializer):
        # При обновлении объявления, возвращаем его на модерацию
        serializer.save(status=0)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Добавляет или убирает продукт из избранного."""
        product = self.get_object()
        user = request.user
        
        favorite, created = Favorite.objects.get_or_create(
            user=user,
            product=product
        )
        
        if not created:
            favorite.delete()
            return Response({'status': 'removed from favorites'})
        
        return Response({'status': 'added to favorites'})
    

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        product = self.get_object()
        user = request.user
        
        # Проверяем, что пользователь является автором
        if product.author != user:
            return Response(
                {'error': 'Вы не являетесь автором этого объявления'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status is None:
            return Response(
                {'error': 'Необходимо указать новый статус'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем допустимые переходы статусов
        valid_transitions = {
            3: [4],  # Из "Опубликовано" можно перейти только в "Архив"
            4: [0],  # Из "Архив" можно перейти только на "Модерацию"
        }
        
        if product.status in valid_transitions and int(new_status) in valid_transitions[product.status]:
            product.status = int(new_status)
            product.save()
            return Response({'status': 'updated'})
        
        return Response(
            {'error': 'Недопустимый переход статуса'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('order')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    @action(detail=True)
    def products(self, request, slug=None):
        category = self.get_object()
        products = Product.objects.filter(category=category, status=3)
        
        # Применяем фильтры
        city_id = request.query_params.get('city')
        if city_id and city_id.isdigit():
            products = products.filter(city_id=city_id)
        
        currency_id = request.query_params.get('currency')
        if currency_id and currency_id.isdigit():
            products = products.filter(currency_id=currency_id)
        
        # Сортировка
        sort = request.query_params.get('sort')
        if sort == 'price_asc':
            products = products.order_by('price')
        elif sort == 'price_desc':
            products = products.order_by('-price')
        elif sort == 'date_asc':
            products = products.order_by('created_at')
        else:
            products = products.order_by('-created_at')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all().order_by('order')
    serializer_class = CurrencySerializer


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all().order_by('name')
    serializer_class = CitySerializer


class FavoriteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related(
            'product', 'product__author', 'product__category', 'product__currency', 'product__city'
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить информацию о текущем пользователе"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)