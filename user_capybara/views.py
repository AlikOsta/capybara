from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, TemplateView, UpdateView
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.urls import reverse_lazy, reverse

from app.models import Product
from .forms import UserProfileForm

User = get_user_model()

class AuthorProfileMixin:
    """Миксин для получения автора профиля и проверки прав доступа"""
    
    def get_author(self):
        return get_object_or_404(User, id=self.kwargs['author_id'])
    
    def is_own_profile(self):
        return self.request.user.is_authenticated and self.request.user == self.get_author()


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class AuthorProfileView(AuthorProfileMixin, TemplateView):
    """Представление профиля автора с его объявлениями, разделенными по статусам"""
    template_name = 'user_capybara/author_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.get_author()
        
        context['author'] = author
        context['is_own_profile'] = self.is_own_profile()
        
        # Для других пользователей показываем только опубликованные объявления
        if not context['is_own_profile']:
            context['published_products'] = Product.objects.filter(
                author=author, 
                status=3
            ).select_related('category', 'city', 'currency')
            return context
        
        # Для собственного профиля показываем объявления по статусам
        # Опубликованные (статус 3)
        context['published_products'] = Product.objects.filter(
            author=author, 
            status=3
        ).select_related('category', 'city', 'currency')
        
        # На модерации (статус 0)
        context['pending_products'] = Product.objects.filter(
            author=author, 
            status=0
        ).select_related('category', 'city', 'currency')
        
        # Одобренные, но не опубликованные (статус 1)
        context['approved_products'] = Product.objects.filter(
            author=author, 
            status=1
        ).select_related('category', 'city', 'currency')
        
        # Заблокированные (статус 2)
        context['rejected_products'] = Product.objects.filter(
            author=author, 
            status=2
        ).select_related('category', 'city', 'currency')
        
        # Архивные (статус 4)
        context['archived_products'] = Product.objects.filter(
            author=author, 
            status=4
        ).select_related('category', 'city', 'currency')
        
        return context


class TelegramAuthView(TemplateView):
    """Представление для авторизации через Telegram"""
    template_name = 'user_capybara/telegram_auth.html'
    
class MiniAppView(TemplateView):
    """Представление для Telegram Mini App"""
    template_name = 'user_capybara/mini_app.html'


@method_decorator(login_required(login_url='user:telegram_auth'), name='dispatch')
class UserProfileEditView(UpdateView):
    """Представление для редактирования профиля пользователя"""
    model = User
    form_class = UserProfileForm
    template_name = 'user_capybara/profile_edit.html'
    
    def get_object(self, queryset=None):
        # Редактировать можно только свой профиль
        return self.request.user
    
    def get_success_url(self):
        return reverse('user:author_profile', kwargs={'author_id': self.request.user.id})