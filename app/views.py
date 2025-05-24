from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django_q.tasks import async_task
from django.core.cache import cache
from functools import wraps


from .models import Product, Category, Currency, City, Favorite, ProductView, BannerPost
from .forms import ProductForm


def htmx_aware_login_required(view_func):
    """
    Декоратор, который проверяет авторизацию и корректно обрабатывает HTMX-запросы
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('HX-Request') == 'true':
                return HttpResponse(
                    status=200,
                    headers={
                        'HX-Redirect': reverse('user:telegram_auth')
                    }
                )
            return redirect('user:telegram_auth')
        return view_func(request, *args, **kwargs)
    return wrapper


def index(request):
    context = {
        'categories': Category.objects.all(),
        'currencies': Currency.objects.all(),
        'cities': City.objects.all(),
        'banners': BannerPost.objects.all(),
    }

    if request.headers.get("HX-Request"):
        return render(request, "app/includes/include_index.html", context)
    return render(request, "app/index.html", context)


def product_list(request):
    page = int(request.GET.get("page", 1))
    products = Product.objects.filter(status=3).order_by('-created_at')
    paginator = Paginator(products, 32)
    
    products_page = paginator.get_page(page)
    
    context = {
        "products": products_page,
        "total_count": products.count(),
    }
    
    return render(request, 'app/includes/product_list.html', context)


@htmx_aware_login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.author = request.user
            product.status = 0 
            product.save()

            async_task('app.tasks.moderate_product', product.id)

            return HttpResponse(status=204, headers={'HX-Trigger': 'productListChanged'})
    else:
        form = ProductForm()
    return render(request, 'app/includes/product_form_modal.html', {'form': form})


@htmx_aware_login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.author = request.user
            product.status = 0
            product.save()

            async_task('app.tasks.moderate_product', product.id)

            return HttpResponse(status=204, headers={'HX-Trigger': 'productListChanged'})
    else:
        form = ProductForm(instance=product)

        context = {
            'form': form,
            'is_edit': True,
        }

    return render(request, 'app/includes/product_form_modal.html', context)



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
        if obj.author != request.user:
            return redirect('app:index')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(cache_page(60 * 15), name='dispatch')
class ProductListView(PublishedProductsMixin, SearchMixin, ListView):
    """Представление для списка объявлений."""
    model = Product
    template_name = 'app/index.html'
    context_object_name = 'products'
    paginate_by = 30

    def get_queryset(self):
        queryset = Product.objects.filter(status=3).select_related(
            'author', 'category', 'currency', 'city'
        )

        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().select_related()
        
        context['query'] = self.request.GET.get('q', '')
        context['total_count'] = self.get_queryset().count()
        context['has_more'] = context['total_count'] > len(context['products'])
        context['banners'] = BannerPost.objects.all().select_related('author')

        if self.request.user.is_authenticated:
            favorite_products = list(
                Favorite.objects.filter(user=self.request.user)
                .values_list('product_id', flat=True)
            )
            context['favorite_products'] = favorite_products
        else:
            context['favorite_products'] = []
        return context
    


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
@method_decorator(cache_page(60 * 15), name='dispatch')
class ProductDetailView(DetailView):
    """Представление для детального просмотра объявления."""
    model = Product
    template_name = 'app/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        # Используем select_related для загрузки связанных объектов за один запрос
        return Product.objects.select_related('author', 'category', 'currency', 'city')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if obj.status != 3 and obj.author != self.request.user and not self.request.user.is_staff:
            raise Http404("Объявление не найдено")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_favorite'] = is_favorite(self.request, self.object)
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.user != self.object.author:
            ip_address = self.get_client_ip(request)
            session_key = request.session.session_key

            if not session_key:
                request.session.save()
                session_key = request.session.session_key

            if request.user.is_authenticated:
                ProductView.objects.get_or_create(
                    product=self.object,
                    user=request.user
                )
            else:
                ProductView.objects.get_or_create(
                    product=self.object,
                    ip_address=ip_address,
                    session_key=session_key
                )

        return self.render_to_response(self.get_context_data(object=self.object))

    def get_client_ip(self, request):
        """Получает IP-адрес клиента из запроса"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
@method_decorator(cache_page(60 * 15), name='dispatch')
class CategoryDetailView(PublishedProductsMixin, SearchMixin, ListView):
    """Представление для детального просмотра категории."""
    model = Product
    template_name = 'app/category_detail.html'
    context_object_name = 'products'
    paginate_by = 10 

    def setup(self, request, *args, **kwargs):
        """Инициализация общих данных при настройке представления"""
        super().setup(request, *args, **kwargs)
        self.category = None
        self.base_queryset = None
        self.total_count = None
        self.filtered_queryset = None

    def get_category(self):
        if self.category is None:
            self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return self.category

    def get_base_queryset(self):
        if self.base_queryset is None:
            self.category = self.get_category()
            self.base_queryset = Product.objects.filter(
                status=3, 
                category=self.category
            ).select_related(
                'author', 'category', 'currency', 'city'
            )
        return self.base_queryset

    def apply_filters(self, queryset):
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        city_id = self.request.GET.get('city')
        if city_id and city_id.isdigit():
            queryset = queryset.filter(city_id=city_id)

        currency_id = self.request.GET.get('currency')
        if currency_id and currency_id.isdigit():
            queryset = queryset.filter(currency_id=currency_id)

        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'date_asc':
            queryset = queryset.order_by('created_at')
        else: 
            queryset = queryset.order_by('-created_at')
            
        return queryset

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        queryset = Product.objects.filter(status=3, category=self.category).select_related(
            'author', 'category', 'currency', 'city'
        ).prefetch_related(
            'favorited_by' 
        )

        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        city_id = self.request.GET.get('city')
        if city_id and city_id.isdigit():
            queryset = queryset.filter(city_id=city_id)

        currency_id = self.request.GET.get('currency')
        if currency_id and currency_id.isdigit():
            queryset = queryset.filter(currency_id=currency_id)

        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'date_asc':
            queryset = queryset.order_by('created_at')
        else: 
            queryset = queryset.order_by('-created_at')

        self.total_count = queryset.count()

        return queryset

    def get_context_data(self, **kwargs):

        cities_cache_key = "all_cities"
        currencies_cache_key = "all_currencies"

        cities = cache.get(cities_cache_key)
        if not cities:
            cities = list(City.objects.all())
            cache.set(cities_cache_key, cities, 60*60)  # 1 час

        currencies = cache.get(currencies_cache_key)
        if not currencies:
            currencies = list(Currency.objects.all())
            cache.set(currencies_cache_key, currencies, 60*60)  # 1 час
            
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        context['cities'] = City.objects.all()
        context['currencies'] = Currency.objects.all()
        context['query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', '')
        context['current_city'] = self.request.GET.get('city', '')
        context['current_currency'] = self.request.GET.get('currency', '')
        
        total_count = self.get_queryset().count()
        context['total_count'] = total_count
        context['has_more'] = self.total_count > len(context['products'])
        
        if self.request.user.is_authenticated:
            # Оптимизируем запрос избранных продуктов
            context['favorite_products'] = list(
                Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)
            )
        else:
            context['favorite_products'] = []
        return context



@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class ProductCreateView(CreateView):
    """Представление для создания нового объявления."""
    model = Product
    form_class = ProductForm
    template_name = 'app/product_form.html'
    success_url = reverse_lazy('app:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        # Если запрос от HTMX, возвращаем перенаправление для HTMX
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                status=200,
                headers={
                    'HX-Redirect': self.get_success_url()
                }
            )
        return response
    
    def get_template_names(self):
        # Если запрос от HTMX, используем шаблон для модального окна
        if self.request.headers.get('HX-Request'):
            return ['app/includes/product_form_modal.html']
        return [self.template_name]
    

@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class ProductUpdateView(AuthorRequiredMixin, UpdateView):
    """Представление для редактирования объявления."""
    model = Product
    form_class = ProductForm
    template_name = 'app/product_form.html'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return Product.objects.filter(author=self.request.user)

    def form_valid(self, form):
        form.instance.status = 0 
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('app:product_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True 
        return context
    
    def get_template_names(self):
        # Если запрос от HTMX, используем шаблон для модального окна
        if self.request.headers.get('HX-Request'):
            return ['app/includes/product_form_modal.html']
        return [self.template_name]


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class ProductDeleteView(AuthorRequiredMixin, DeleteView):
    """Представление для удаления объявления."""
    model = Product
    template_name = 'app/product_confirm_delete.html'
    success_url = reverse_lazy('app:index')
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return Product.objects.filter(author=self.request.user)



@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class FavoriteListView(ListView):
    """Представление для отображения избранных объявлений."""
    model = Product
    template_name = 'app/favorites.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(
            favorited_by__user=self.request.user,
            status=3 
        ).select_related(
            'category', 'city', 'currency', 'author'
        ).prefetch_related(
            'favorited_by'
        ).distinct() 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Избранное'
        context['has_more'] = self.get_queryset().count() > len(context['products'])
        return context
    

@login_required(login_url='user:telegram_auth')
@require_POST
def toggle_favorite(request, pk):
    """Добавляет или удаляет объявление из избранного."""
    product = get_object_or_404(Product, pk=pk)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )
    if not created:
        favorite.delete()
        is_fav = False
    else:
        is_fav = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_fav,
            'count': product.favorited_by.count()
        })
    return redirect('app:product_detail', pk=pk)


def is_favorite(request, product):
    """Проверяет, находится ли объявление в избранном у пользователя."""
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
    if request.user != product.author:
        return redirect('app:product_detail', pk=pk)

    valid_transitions = {
        3: [4],  # Из "Опубликовано" можно перейти только в "Архив"
        4: [0],  # Из "Архив" можно перейти только на "Модерацию"
    }
    if product.status in valid_transitions and status in valid_transitions[product.status]:
        product.status = status
        product.save()

    return redirect('app:product_detail', pk=pk)


class ProductListAPIView(View):
    """API представление для получения списка объявлений."""
    def get(self, request, *args, **kwargs):
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))
        query = request.GET.get('q', '')
        
        queryset = Product.objects.filter(status=3).select_related(
            'author', 'category', 'currency', 'city'
        )
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        
        total_count = queryset.count()
        products = queryset.order_by('-created_at')[offset:offset + limit]
        
        favorite_products = []
        if request.user.is_authenticated:
            favorite_products = list(request.user.favorites.values_list('product_id', flat=True))
            
        html = render_to_string(
            'app/includes/product_cards_list.html',
            {
                'products': products,
                'favorite_products': favorite_products,
                'request': request
            }
        )
        
        has_more = (offset + limit) < total_count
        return JsonResponse({
            'html': html,
            'has_more': has_more,
            'total_count': total_count,
            'next_offset': offset + limit if has_more else None
        })



class CategoryProductsAPIView(View):
    """API представление для получения списка объявлений в категории."""

    def get(self, request, *args, **kwargs):
        category_slug = kwargs.get('category_slug')
        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Категория не найдена'}, status=404)

        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))
        query = request.GET.get('q', '')
        city_id = request.GET.get('city')
        currency_id = request.GET.get('currency')
        sort = request.GET.get('sort', '')
        
        queryset = Product.objects.filter(status=3, category=category).select_related(
            'author', 'category', 'currency', 'city'
        )
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
            
        if city_id and city_id.isdigit():
            queryset = queryset.filter(city_id=city_id)
            
        if currency_id and currency_id.isdigit():
            queryset = queryset.filter(currency_id=currency_id)

        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'date_asc':
            queryset = queryset.order_by('created_at')
        else:  
            queryset = queryset.order_by('-created_at')

        total_count = queryset.count()
        products = queryset[offset:offset + limit]
        
        favorite_products = []
        if request.user.is_authenticated:
            favorite_products = list(request.user.favorites.values_list('product_id', flat=True))
            
        html = render_to_string(
            'app/includes/product_cards_list.html',
            {
                'products': products,
                'favorite_products': favorite_products,
                'request': request
            }
        )
        
        has_more = (offset + limit) < total_count
        return JsonResponse({
            'html': html,
            'has_more': has_more,
            'total_count': total_count,
            'next_offset': offset + limit if has_more else None
        })


class FavoriteProductsAPIView(View):
    """API представление для получения списка избранных объявлений."""
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Требуется авторизация'}, status=401)
            
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))
        
        queryset = Product.objects.filter(
            favorited_by__user=request.user,
            status=3
        ).select_related('author', 'category', 'currency', 'city')
        
        total_count = queryset.count()
        products = queryset.order_by('-created_at')[offset:offset + limit]
        
        html = render_to_string(
            'app/includes/product_cards_list.html',
            {
                'products': products,
                'favorite_products': list(request.user.favorites.values_list('product_id', flat=True)),
                'request': request
            }
        )
        
        has_more = (offset + limit) < total_count
        return JsonResponse({
            'html': html,
            'has_more': has_more,
            'total_count': total_count,
            'next_offset': offset + limit if has_more else None
        })


def banner_ad_info(request):
    """Представление для отображения информации о размещении рекламы."""
    admin_telegram = "@newpunknot"  
    return render(request, 'app/includes/banner_ad_modal.html', {
        'admin_telegram': admin_telegram
    })
