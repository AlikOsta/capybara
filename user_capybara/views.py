from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from app.models import Product
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class AuthorProfileView(ListView):
    model = Product
    template_name = 'user_capybara/author_profile.html'
    context_object_name = 'products'

    def get_queryset(self):
        author = get_object_or_404(get_user_model(), id=self.kwargs['author_id'])
        return Product.objects.filter(author=author, status=3) 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_object_or_404(get_user_model(), id=self.kwargs['author_id'])
        context['author'] = author
        context['is_own_profile'] = self.request.user == author
        if context['is_own_profile']:
            context['pending_products'] = Product.objects.filter(
                author=author, 
                status=0
            )
        return context


class TelegramAuthView(TemplateView):
    template_name = 'user_capybara/telegram_auth.html'