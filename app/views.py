from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseRedirect

from .models import Product, Category, Currency, City, Favorite, ProductView
from .forms import ProductForm

# Миксин для фильтрации опубликованных объявлений
class PublishedProductsMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status=3)  # Опубликованные объявления

# Миксин для поиска
class SearchMixin:
    def apply_search_filter(self, queryset):
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        return queryset, query

# Миксин для проверки авторства
class AuthorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('app:index')
        return super().dispatch(request, *args, **kwargs)


# Список всех объявлений
class ProductListView(PublishedProductsMixin, SearchMixin, ListView):
    model = Product
    template_name = 'app/index.html'
    context_object_name = 'products'
    paginate_by = 10  # Начальное количество объявлений
    
    def get_queryset(self):
        queryset = Product.objects.filter(status=3)  # Только опубликованные
        
        # Применяем поиск, если есть запрос
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем категории
        context['categories'] = Category.objects.all()
        
        # Добавляем поисковый запрос
        context['query'] = self.request.GET.get('q', '')
        
        # Получаем общее количество объявлений
        context['total_count'] = self.get_queryset().count()
        
        # Определяем, есть ли еще объявления для загрузки
        context['has_more'] = context['total_count'] > len(context['products'])
        
        # Получаем список ID избранных объявлений для текущего пользователя
        if self.request.user.is_authenticated:
            context['favorite_products'] = list(
                self.request.user.favorites.values_list('product_id', flat=True)
            )
        else:
            context['favorite_products'] = []
        
        return context


# Детальное представление объявления
@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class ProductDetailView(DetailView):
    model = Product
    template_name = 'app/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Проверяем, может ли пользователь просматривать это объявление
        if obj.status != 3 and obj.author != self.request.user and not self.request.user.is_staff:
            raise Http404("Объявление не найдено")
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем информацию о том, находится ли объявление в избранном
        context['is_favorite'] = is_favorite(self.request, self.object)
        return context
    
    def get(self, request, *args, **kwargs):
        # Получаем объект
        self.object = self.get_object()
        
        # Учитываем просмотр, только если это не автор объявления
        if request.user != self.object.author:
            # Получаем IP-адрес и ключ сессии
            ip_address = self.get_client_ip(request)
            session_key = request.session.session_key
            
            # Если сессия не создана, создаем ее
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
            
            # Создаем запись о просмотре, если она еще не существует
            if request.user.is_authenticated:
                # Для авторизованных пользователей
                ProductView.objects.get_or_create(
                    product=self.object,
                    user=request.user
                )
            else:
                # Для анонимных пользователей
                ProductView.objects.get_or_create(
                    product=self.object,
                    ip_address=ip_address,
                    session_key=session_key
                )
        
        # Продолжаем стандартную обработку запроса
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    
    def get_client_ip(self, request):
        """Получает IP-адрес клиента из запроса"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Список объявлений в категории
class CategoryDetailView(PublishedProductsMixin, SearchMixin, ListView):
    model = Product
    template_name = 'app/category_detail.html'
    context_object_name = 'products'
    paginate_by = 10  # Начальное количество объявлений
    
    def get_queryset(self):
        # Получаем категорию по slug
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        
        # Базовый QuerySet
        queryset = Product.objects.filter(status=3, category=self.category)
        
        # Применяем поиск, если есть запрос
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )
        
        # Применяем фильтры
        city_id = self.request.GET.get('city')
        if city_id and city_id.isdigit():
            queryset = queryset.filter(city_id=city_id)
        
        currency_id = self.request.GET.get('currency')
        if currency_id and currency_id.isdigit():
            queryset = queryset.filter(currency_id=currency_id)
        
        # Применяем сортировку
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'date_asc':
            queryset = queryset.order_by('created_at')
        elif sort == 'date_desc':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем категорию
        context['category'] = self.category
        
        # Добавляем города и валюты для фильтров
        context['cities'] = City.objects.all()
        context['currencies'] = Currency.objects.all()
        
        # Добавляем текущие параметры фильтрации
        context['query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', '')
        context['current_city'] = self.request.GET.get('city', '')
        context['current_currency'] = self.request.GET.get('currency', '')
        
        # Получаем общее количество объявлений
        context['total_count'] = self.get_queryset().count()
        
        # Определяем, есть ли еще объявления для загрузки
        context['has_more'] = context['total_count'] > len(context['products'])
        
        # Получаем список ID избранных объявлений для текущего пользователя
        if self.request.user.is_authenticated:
            context['favorite_products'] = list(
                self.request.user.favorites.values_list('product_id', flat=True)
            )
        else:
            context['favorite_products'] = []
        
        return context

    

# Создание объявления
@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'app/product_form.html'
    success_url = reverse_lazy('app:index')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    

# Обновление объявления
@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class ProductUpdateView(AuthorRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'app/product_form.html'
    pk_url_kwarg = 'pk'
    
    def get_success_url(self):
        return reverse_lazy('app:product_detail', kwargs={'pk': self.object.pk})
    
    def get_queryset(self):
        # Пользователь может редактировать только свои объявления
        return Product.objects.filter(author=self.request.user)
    
    def form_valid(self, form):
        # При любом редактировании отправляем объявление на модерацию
        form.instance.status = 0  # Устанавливаем статус "На модерации"
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True  # Флаг для шаблона, чтобы различать создание и редактирование
        return context


# Удаление объявления
@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class ProductDeleteView(AuthorRequiredMixin, DeleteView):
    model = Product
    template_name = 'app/product_confirm_delete.html'
    success_url = reverse_lazy('app:index')
    pk_url_kwarg = 'pk'
    
    def get_queryset(self):
        return Product.objects.filter(author=self.request.user)


# Добавить класс представления для списка избранных объявлений
@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class FavoriteListView(ListView):
    model = Product
    template_name = 'app/favorites.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        # Получаем только избранные объявления текущего пользователя
        return Product.objects.filter(
            favorited_by__user=self.request.user,
            status=3  # Только опубликованные
        ).select_related('category', 'city', 'currency', 'author')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Избранное'
        return context
    
    
# Добавить функцию для добавления/удаления из избранного
@login_required(login_url='user:telegram_auth')
@require_POST
def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk)
     # Проверяем, есть ли уже это объявление в избранном
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    # Если объявление уже было в избранном, удаляем его
    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True
    
    # Если запрос через AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'count': product.favorited_by.count()
        })
    
    # Иначе перенаправляем обратно на страницу объявления
    return redirect('app:product_detail', pk=pk)

# Добавить функцию для проверки, находится ли объявление в избранном
def is_favorite(request, product):
    if not request.user.is_authenticated:
        return False
    return Favorite.objects.filter(user=request.user, product=product).exists()


@login_required(login_url='user:telegram_auth')
@require_POST
def change_product_status(request, pk, status):
    """
    Изменяет статус объявления.
    Доступные статусы:
    0 - На модерации
    1 - Одобрено
    2 - Отклонено
    3 - Опубликовано
    4 - Архив
    """
    product = get_object_or_404(Product, pk=pk)
    
    # Проверяем, что пользователь является автором объявления
    if request.user != product.author:
        return redirect('app:product_detail', pk=pk)
    
    # Проверяем допустимость перехода между статусами
    valid_transitions = {
        3: [4],  # Из "Опубликовано" можно перейти только в "Архив"
        4: [0],  # Из "Архив" можно перейти только на "Модерацию" (0)
    }
    
    # Если текущий статус есть в словаре и новый статус допустим
    if product.status in valid_transitions and status in valid_transitions[product.status]:
        product.status = status
        product.save()
    
    return redirect('app:product_detail', pk=pk)


class ProductListAPIView(View):
    """API представление для получения списка объявлений"""
    
    def get(self, request, *args, **kwargs):
        # Получаем параметры запроса
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))
        query = request.GET.get('q', '')
        
        # Базовый QuerySet
        queryset = Product.objects.filter(status=3)  # Только опубликованные
        
        # Применяем поиск, если есть запрос
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )
        
        # Получаем общее количество объявлений
        total_count = queryset.count()
        
        # Применяем пагинацию
        products = queryset.order_by('-created_at')[offset:offset+limit]
        
        # Получаем список ID избранных объявлений для текущего пользователя
        favorite_products = []
        if request.user.is_authenticated:
            favorite_products = list(request.user.favorites.values_list('product_id', flat=True))
        
        # Рендерим HTML для карточек объявлений
        html = render_to_string(
            'app/includes/product_cards_list.html',
            {
                'products': products,
                'favorite_products': favorite_products,
                'request': request
            }
        )
        
        # Определяем, есть ли еще объявления для загрузки
        has_more = (offset + limit) < total_count
        
        # Возвращаем JSON-ответ
        return JsonResponse({
            'html': html,
            'has_more': has_more,
            'total_count': total_count,
            'next_offset': offset + limit if has_more else None
        })

class CategoryProductsAPIView(View):
    """API представление для получения списка объявлений в категории"""
    
    def get(self, request, *args, **kwargs):
        # Получаем категорию по slug
        category_slug = kwargs.get('category_slug')
        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Категория не найдена'}, status=404)
        
        # Получаем параметры запроса
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))
        query = request.GET.get('q', '')
        sort = request.GET.get('sort', '')
        city_id = request.GET.get('city', '')
        currency_id = request.GET.get('currency', '')
        
        # Базовый QuerySet
        queryset = Product.objects.filter(status=3, category=category)
        
        # Применяем поиск, если есть запрос
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )
        
        # Применяем фильтры
        if city_id and city_id.isdigit():
            queryset = queryset.filter(city_id=city_id)
        
        if currency_id and currency_id.isdigit():
            queryset = queryset.filter(currency_id=currency_id)
        
        # Применяем сортировку
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'date_asc':
            queryset = queryset.order_by('created_at')
        elif sort == 'date_desc':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        # Получаем общее количество объявлений
        total_count = queryset.count()
        
        # Применяем пагинацию
        products = queryset[offset:offset+limit]
        
        # Получаем список ID избранных объявлений для текущего пользователя
        favorite_products = []
        if request.user.is_authenticated:
            favorite_products = list(request.user.favorites.values_list('product_id', flat=True))
        
        # Рендерим HTML для карточек объявлений
        html = render_to_string(
            'app/includes/product_cards_list.html',
            {
                'products': products,
                'favorite_products': favorite_products,
                'request': request
            }
        )
        
        # Определяем, есть ли еще объявления для загрузки
        has_more = (offset + limit) < total_count
        
        # Возвращаем JSON-ответ
        return JsonResponse({
            'html': html,
            'has_more': has_more,
            'total_count': total_count,
            'next_offset': offset + limit if has_more else None
        })
