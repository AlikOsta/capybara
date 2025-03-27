from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

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
        if obj.author != request.user:
            return redirect('app:index')
        return super().dispatch(request, *args, **kwargs)


# Кэширование главной страницы на 15 минут
# @method_decorator(cache_page(60 * 2), name='dispatch')
class ProductListView(PublishedProductsMixin, SearchMixin, ListView):
    """Представление для списка объявлений."""
    model = Product
    template_name = 'app/index.html'
    context_object_name = 'products'
    paginate_by = 10 

    def get_queryset(self):
        # Используем select_related для загрузки связанных объектов за один запрос
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
        context['categories'] = Category.objects.all()
        context['query'] = self.request.GET.get('q', '')
        context['total_count'] = self.get_queryset().count()
        context['has_more'] = context['total_count'] > len(context['products'])

        if self.request.user.is_authenticated:
            context['favorite_products'] = list(
                self.request.user.favorites.values_list('product_id', flat=True)
            )
        else:
            context['favorite_products'] = []
        return context


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
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


# Кэширование страницы категории на 15 минут
@method_decorator(cache_page(60 * 15), name='dispatch')
class CategoryDetailView(PublishedProductsMixin, SearchMixin, ListView):
    """Представление для детального просмотра категории."""
    model = Product
    template_name = 'app/category_detail.html'
    context_object_name = 'products'
    paginate_by = 10 

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        # Используем select_related для загрузки связанных объектов за один запрос
        queryset = Product.objects.filter(status=3, category=self.category).select_related(
            'author', 'category', 'currency', 'city'
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

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['cities'] = City.objects.all()
        context['currencies'] = Currency.objects.all()
        context['query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', '')
        context['current_city'] = self.request.GET.get('city', '')
        context['current_currency'] = self.request.GET.get('currency', '')
        context['total_count'] = self.get_queryset().count()
        context['has_more'] = context['total_count'] > len(context['products'])
        if self.request.user.is_authenticated:
            context['favorite_products'] = list(
                self.request.user.favorites.values_list('product_id', flat=True)
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
        return super().form_valid(form)


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
    paginate_by = 10

    def get_queryset(self):
        # Используем prefetch_related для оптимизации запроса избранных объявлений
        return Product.objects.filter(
            favorited_by__user=self.request.user,
            status=3 
        ).select_related('category', 'city', 'currency', 'author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Избранное'
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
        
        # Используем select_related для загрузки связанных объектов за один запрос
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
