from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseRedirect

from .models import Product, Category, Currency, City, Favorite
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
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('author', 'category', 'city', 'currency')
        queryset, _ = self.apply_search_filter(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['query'] = self.request.GET.get('q', '')
        return context


# Детальное представление объявления
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


# Список объявлений в категории
class CategoryDetailView(PublishedProductsMixin, SearchMixin, ListView):
    model = Product
    template_name = 'app/category_detail.html'
    context_object_name = 'products'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            category__slug=self.kwargs['category_slug']
        ).select_related('category', 'city', 'currency', 'author')

        # Поиск
        queryset, _ = self.apply_search_filter(queryset)
        
        # Сортировка
        sort_options = {
            'price_asc': 'price',
            'price_desc': '-price',
            'date_desc': '-created_at',
            'date_asc': 'created_at'
        }
        sort = self.request.GET.get('sort')
        if sort in sort_options:
            queryset = queryset.order_by(sort_options[sort])
        
        # Фильтры
        filters = {}
        if city := self.request.GET.get('city'):
            filters['city__id'] = city
        if currency := self.request.GET.get('currency'):
            filters['currency__id'] = currency

        return queryset.filter(**filters)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        context.update({
            'query': self.request.GET.get('q', ''),
            'current_sort': self.request.GET.get('sort'),
            'current_city': self.request.GET.get('city'),
            'current_currency': self.request.GET.get('currency'),
            'cities': City.objects.all(),
            'currencies': Currency.objects.all(),
        })
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
class ProductUpdateView(UpdateView):
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