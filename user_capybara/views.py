from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, TemplateView, UpdateView
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.urls import reverse_lazy, reverse
import logging
logger = logging.getLogger(__name__)

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
    
    def setup(self, request, *args, **kwargs):
        """Инициализация общих данных при настройке представления"""
        super().setup(request, *args, **kwargs)
        self._author = None
        self._is_own_profile = None
        self._products_by_status = None
    
    def get_template_names(self):
        """
        Возвращает имя шаблона в зависимости от типа запроса.
        Если запрос через HTMX, используется частичный шаблон,
        иначе - полный шаблон.
        """
        # Проверяем, является ли запрос HTMX-запросом
        if self.request.headers.get('HX-Request') == 'true':
            return ['user_capybara/author_profile.html']
        else:
            return ['user_capybara/author_profile_full.html']
    
    def get_author(self):
        """Получает автора профиля (с кэшированием результата)"""
        if self._author is None:
            try:
                author_id = self.kwargs.get('author_id')
                logger.info(f"Getting author with ID: {author_id}")
                self._author = get_object_or_404(User, id=author_id)
                logger.info(f"Found author: {self._author.username}")
            except Exception as e:
                logger.error(f"Error getting author: {e}")
                raise
        return self._author
    
    def is_own_profile(self):
        """Проверяет, является ли профиль собственным (с кэшированием результата)"""
        if self._is_own_profile is None:
            try:
                self._is_own_profile = self.request.user.is_authenticated and self.request.user.id == self.get_author().id
                logger.info(f"Is own profile: {self._is_own_profile}")
            except Exception as e:
                logger.error(f"Error checking if own profile: {e}")
                self._is_own_profile = False
        return self._is_own_profile
    
    def get_products_by_status(self):
        """Получает все продукты автора, сгруппированные по статусу (с кэшированием результата)"""
        if self._products_by_status is None:
            author = self.get_author()
            
            all_products = Product.objects.filter(
                author=author
            ).select_related('category', 'city', 'currency', 'author')

            self._products_by_status = {
                0: [], # pending
                1: [], # approved
                2: [], # rejected
                3: [], # published
                4: [], # archived
            }
            
            for product in all_products:
                self._products_by_status[product.status].append(product)
                
        return self._products_by_status
    
    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            author = self.get_author()
            is_own_profile = self.is_own_profile()
            
            context['author'] = author
            context['is_own_profile'] = is_own_profile
            
            products_by_status = self.get_products_by_status()
            
            # Добавляем в контекст только нужные продукты
            context['published_products'] = products_by_status[3]
            
            if is_own_profile:
                context['pending_products'] = products_by_status[0]
                context['approved_products'] = products_by_status[1]
                context['rejected_products'] = products_by_status[2]
                context['archived_products'] = products_by_status[4]
            
            return context
        except Exception as e:
            logger.error(f"Error in get_context_data: {e}")
            return {'author': self.get_author(), 'is_own_profile': False}



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
        return self.request.user
    
    def get_success_url(self):
        return reverse('user:author_profile', kwargs={'author_id': self.request.user.id})