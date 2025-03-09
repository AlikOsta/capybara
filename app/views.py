from django.shortcuts import render
from .models import Product, Category, Currency, City
from django.views.generic import ListView, DetailView
from django.db.models import Q

class ProductListView(ListView):
    model = Product
    template_name = 'app/index.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
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
        queryset = Product.objects.filter(category__slug=self.kwargs['category_slug'])
        
        # Search
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) 
            )
            
        # Sorting
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'date_desc':
            queryset = queryset.order_by('-created_at')
        elif sort == 'date_asc':
            queryset = queryset.order_by('created_at')
            
        # City filter
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city__id=city)
            
        # Currency filter
        currency = self.request.GET.get('currency')
        if currency:
            queryset = queryset.filter(currency__id=currency)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(slug=self.kwargs['category_slug'])
        context['query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', '')
        context['current_city'] = self.request.GET.get('city', '')
        context['current_currency'] = self.request.GET.get('currency', '')
        context['cities'] = City.objects.all()
        context['currencies'] = Currency.objects.all()
        return context


