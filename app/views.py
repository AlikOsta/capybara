from django.shortcuts import render
from .models import Product, Category
from django.views.generic import ListView, DetailView


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