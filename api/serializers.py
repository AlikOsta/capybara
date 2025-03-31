from rest_framework import serializers
from app.models import Product, Category, Currency, City, Favorite, ProductView
from django.db.models import Count, Case, When, BooleanField, Value
from user_capybara.models import TelegramUser
from django.contrib.auth import get_user_model
from rest_framework import generics

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Преобразует объекты модели TelegramUser в JSON и обратно."""
    class Meta:
        model = User # модель, которую мы сериализуем
        fields = ['id', 'telegram_id', 'username', 'first_name', 'last_name', 'photo_url'] #  поля, которые нужно включить в API-ответ
        read_only_fields = ['telegram_id'] #только для чтения,


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def validate_first_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("first_name не может быть пустым.")
        return value
        

class CategorySerializer(serializers.ModelSerializer):
    """Преобразует объекты модели Category в JSON и обратно."""
    class Meta:
        model = Category # модель, которую мы сериализуем
        fields = ['id', 'name', 'slug', 'image', 'order'] #  поля, которые нужно включить в API-ответ


class CurrencySerializer(serializers.ModelSerializer):
    """Преобразует объекты модели Currency в JSON и обратно."""
    class Meta:
        model = Currency
        fields = ['id', 'name', 'code', 'order']


class CitySerializer(serializers.ModelSerializer):
    """Преобразует объекты модели City в JSON и обратно."""
    class Meta:
        model = City
        fields = ['id', 'name']


class ProductListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    is_favorite = serializers.BooleanField(read_only=True)
    view_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'image', 'price', 
            'created_at', 'updated_at', 'status', 'author', 
            'category', 'currency', 'city', 'is_favorite', 'view_count'
        ]
    
    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, product=obj).exists()
        return False
    
    def get_view_count(self, obj):
        return obj.get_view_count()
    

class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.all()

        # Аннотация для is_favorite
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorite=Case(
                    When(favorite__user=user, then=True),
                    default=False,
                    output_field=BooleanField()
                )
            )
        else:
            queryset = queryset.annotate(is_favorite=Value(False, output_field=BooleanField()))

        # Аннотация для view_count
        queryset = queryset.annotate(view_count=Count('productview'))

        return queryset


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления объектов Product."""

    class Meta:
        model = Product
        fields = [
            'category', 'title', 'description', 'image', 
            'price', 'currency', 'city'
        ]
    
    def validate_image(self, value):
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("Изображение не должно превышать 2MB.")
        return value
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной.")
        return value


class ProductDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра объектов Product."""
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField()
    view_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'image', 'price', 
            'created_at', 'updated_at', 'status', 'author', 
            'category', 'currency', 'city', 'is_favorite', 'view_count'
        ]
    
    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, product=obj).exists()
        return False
    
    def get_view_count(self, obj):
        return obj.get_view_count()

class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'product', 'created_at']
