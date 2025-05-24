from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, JsonResponse, Http404
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


# Helper to cache reference lists
CACHE_TTL = 60 * 60  # 1 hour
def get_cached(key, queryset):
    data = cache.get(key)
    if data is None:
        data = list(queryset)
        cache.set(key, data, CACHE_TTL)
    return data

# HTMX-aware login decorator
def htmx_aware_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('HX-Request') == 'true':
                return HttpResponse(status=200, headers={'HX-Redirect': reverse('user:telegram_auth')})
            return redirect('user:telegram_auth')
        return view_func(request, *args, **kwargs)
    return wrapper


def index(request):
    favorite_products = set()
    if request.user.is_authenticated:
        favorite_products = set(
            Favorite.objects.filter(user=request.user)
                    .values_list('product_id', flat=True)
        )
    
    context = {
        'categories': get_cached('all_categories', Category.objects.all()),
        'banners': BannerPost.objects.select_related('author').all(),
        'total_count': cache.get_or_set(
            'products_total_count', 
            lambda: Product.objects.filter(status=3).count(), 
            60 * 5
        ),
        # Возвращаем загрузку первых продуктов!
        'initial_products': cache.get_or_set(
            'initial_products',
            lambda: list(Product.objects.filter(status=3)
                        .select_related('author', 'category', 'currency', 'city')
                        .prefetch_related('favorited_by')[:8]),
            60 * 2
        ),
        'favorite_products': favorite_products,
    }
    
    if request.headers.get("HX-Request"):
        return render(request, "app/includes/include_index.html", context)
    return render(request, "app/index.html", context)




# Mixins
class PublishedMixin:
    def get_queryset(self):
        return super().get_queryset().filter(status=3)

class SearchMixin:
    def filter_search(self, qs):
        q = self.request.GET.get('q')
        if q:
            return qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs

class AuthorRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            return redirect('app:index')
        return super().dispatch(request, *args, **kwargs)


def product_list(request):
    page = int(request.GET.get('page', 1))
    offset = int(request.GET.get('offset', 0))
    
    base_qs = Product.objects.filter(status=3)
    base_qs = base_qs.select_related('author', 'category', 'currency', 'city')
    total = base_qs.count()
    
    limit = 16
    products = base_qs.order_by('-created_at')[offset:offset+limit]
    
    favorite_products = set()
    if request.user.is_authenticated:
        favorite_products = set(
            Favorite.objects.filter(user=request.user)
                    .values_list('product_id', flat=True)
        )
    
    # Создаем объект для совместимости с шаблоном
    class ProductPage:
        def __init__(self, products, offset, limit, total):
            self.object_list = products
            self.has_next = offset + limit < total
            self.next_offset = offset + limit if self.has_next else None
    
    products_page = ProductPage(products, offset, limit, total)
    
    context = {
        'products': products_page,
        'total_count': total,
        'next_offset': products_page.next_offset,
        'favorite_products': favorite_products,  # Добавляем избранные
    }
    return render(request, 'app/includes/product_list.html', context)



@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
@method_decorator(cache_page(60 * 3), name='dispatch')
class ProductDetailView(DetailView):
    model = Product
    template_name = 'app/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.select_related('author', 'category', 'currency', 'city')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.status != 3 and obj.author != self.request.user and not self.request.user.is_staff:
            raise Http404
        return obj

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user != self.object.author:
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR')
            session_key = request.session.session_key or request.session.save() or request.session.session_key
            ProductView.objects.update_or_create(
                product=self.object,
                defaults={'user': request.user} if request.user.is_authenticated else {
                    'ip_address': ip,
                    'session_key': session_key
                }
            )
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_favorite'] = Favorite.objects.filter(user=self.request.user, product=self.object).exists() if self.request.user.is_authenticated else False
        return ctx


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
@method_decorator(cache_page(60 * 15), name='dispatch')
class CategoryDetailView(PublishedMixin, SearchMixin, ListView):
    model = Product
    template_name = 'app/category_detail.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_category(self):
        return get_object_or_404(Category, slug=self.kwargs['category_slug'])

    def get_queryset(self):
        cat = self.get_category()
        qs = Product.objects.filter(status=3, category=cat)
        qs = qs.select_related('author', 'category', 'currency', 'city')
        qs = qs.prefetch_related('favorited_by')
        qs = self.filter_search(qs)
        city = self.request.GET.get('city')
        if city and city.isdigit(): qs = qs.filter(city_id=city)
        cur = self.request.GET.get('currency')
        if cur and cur.isdigit(): qs = qs.filter(currency_id=cur)
        sort = self.request.GET.get('sort')
        ordering = {'price_asc':'price','price_desc':'-price','date_asc':'created_at'}.get(sort, '-created_at')
        qs = qs.order_by(ordering)
        self.total_count = qs.count()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'category': self.get_category(),
            'cities': get_cached('all_cities', City.objects.all()),
            'currencies': get_cached('all_currencies', Currency.objects.all()),
            'total_count': self.total_count,
            'has_more': self.total_count > len(ctx['products']),
            'query': self.request.GET.get('q', ''),
            'current_sort': self.request.GET.get('sort', ''),
            'current_city': self.request.GET.get('city', ''),
            'current_currency': self.request.GET.get('currency', ''),
            'favorite_products': set(
                Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)
            ) if self.request.user.is_authenticated else set(),
        })
        return ctx


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'app/product_form.html'
    success_url = reverse_lazy('app:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = 0
        response = super().form_valid(form)

        async_task('app.tasks.moderate_product', self.object.id)
        
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                status=204, 
                headers={
                    'HX-Trigger': 'productListChanged',
                    'HX-Redirect': self.get_success_url()
                }
            )
        
        return response

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['app/includes/product_form_modal.html']
        return [self.template_name]


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class ProductUpdateView(AuthorRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'app/product_form.html'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return Product.objects.filter(author=self.request.user)

    def form_valid(self, form):
        form.instance.status = 0
        response = super().form_valid(form)

        async_task('app.tasks.moderate_product', self.object.id)
        
        if self.request.headers.get('HX-Request'):
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': 'productListChanged',
                    'HX-Redirect': self.get_success_url()
                }
            )
        
        return response

    def get_success_url(self):
        return reverse_lazy('app:product_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx['is_edit'] = True
        return ctx

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['app/includes/product_form_modal.html']
        return [self.template_name]


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class ProductDeleteView(AuthorRequiredMixin, DeleteView):
    model = Product
    template_name = 'app/product_confirm_delete.html'
    success_url = reverse_lazy('app:index')

    def get_queryset(self):
        return Product.objects.filter(author=self.request.user)


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
@method_decorator(cache_page(60 * 3), name='dispatch')
class FavoriteListView(ListView):
    model = Product
    template_name = 'app/favorites.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(
            favorited_by__user=self.request.user,
            status=3
        ).select_related('category','city','currency','author').prefetch_related('favorited_by').distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        total = self.get_queryset().count()
        ctx.update({
            'title': 'Избранное',
            'has_more': total > len(ctx['products']),
        })
        return ctx


@login_required(login_url='user:telegram_auth')
@require_POST
def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created: fav.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'is_favorite': created, 'count': product.favorited_by.count()})
    return redirect('app:product_detail', pk=pk)


@login_required(login_url='user:telegram_auth')
@require_POST
def change_product_status(request, pk, status):
    product = get_object_or_404(Product, pk=pk)
    transitions = {3:[4],4:[0]}
    if request.user == product.author and status in transitions.get(product.status, []):
        product.status = status
        product.save()
    return redirect('app:product_detail', pk=pk)


class FavoriteProductsAPIView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error':'Требуется авторизация'},status=401)
        offset, limit = map(int, (request.GET.get('offset',0), request.GET.get('limit',10)))
        qs = Product.objects.filter(favorited_by__user=request.user, status=3)
        qs = qs.select_related('author','category','currency','city')
        total = qs.count()
        items = qs.order_by('-created_at')[offset:offset+limit]
        fav_ids = list(request.user.favorites.values_list('product_id', flat=True))
        html = render_to_string('app/includes/product_cards_list.html', {'products':items,'favorite_products':fav_ids,'request':request})
        return JsonResponse({'html':html,'has_more':offset+limit<total,'total_count':total,'next_offset':offset+limit if offset+limit<total else None})


@login_required(login_url='user:telegram_auth')
def banner_ad_info(request):
    return render(request, 'app/includes/banner_ad_modal.html', {'admin_telegram': '@newpunknot'})


@cache_page(60 * 5)
def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    context = {
        'category': category,
        'cities': get_cached('all_cities', City.objects.all()),
        'currencies': get_cached('all_currencies', Currency.objects.all()),
        'total_count': cache.get_or_set(
            f'category_{category_slug}_count',
            lambda: Product.objects.filter(status=3, category=category).count(),
            60 * 5
        ),
    }
    
    return render(request, "app/category_detail.html", context)


def category_product_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 8))
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '')
    city = request.GET.get('city', '')
    currency = request.GET.get('currency', '')
    
    qs = Product.objects.filter(status=3, category=category)
    qs = qs.select_related('author', 'category', 'currency', 'city')
    
    if query:
        qs = qs.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    
    if city and city.isdigit():
        qs = qs.filter(city_id=city)

    if currency and currency.isdigit():
        qs = qs.filter(currency_id=currency)
    
    ordering = {
        'date_desc': '-created_at',
        'date_asc': 'created_at',
        'price_asc': 'price',
        'price_desc': '-price'
    }.get(sort, '-created_at')
    
    qs = qs.order_by(ordering)

    total = qs.count()
    products = qs[offset:offset+limit]
    
    favorite_products = set(
        Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
    ) if request.user.is_authenticated else set()
    

    filter_params = []
    if query:
        filter_params.append(f'q={query}')
    if sort:
        filter_params.append(f'sort={sort}')
    if city:
        filter_params.append(f'city={city}')
    if currency:
        filter_params.append(f'currency={currency}')
    
    filter_string = '&'.join(filter_params)
    
    context = {
        'products': products,
        'category_slug': category_slug,
        'has_more': offset + limit < total,
        'next_offset': offset + limit if offset + limit < total else None,
        'favorite_products': favorite_products,
        'query': query,
        'current_sort': sort,
        'current_city': city,
        'current_currency': currency,
        'filter_params': filter_string,
    }
    
    return render(request, 'app/includes/category_products_list.html', context)
