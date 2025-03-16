from django.shortcuts import render
from .models import Product, Category, Currency, City
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .forms import ProductForm
from django.contrib.auth import get_user_model


class ProductListView(ListView):
    model = Product
    template_name = 'app/index.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(status=3)
        query = self.request.GET.get('q', '')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['query'] = self.request.GET.get('q', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'app/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'


class CategoryDetailView(ListView):
    model = Product
    template_name = 'app/category_detail.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        queryset = Product.objects.filter(
            category__slug=self.kwargs['category_slug']
        ).select_related('category', 'city', 'currency')

        # Поиск
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )
        
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
        
        # Фильтры (город, валюта)
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
    

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'app/product_form.html'
    success_url = reverse_lazy('app:index')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    

