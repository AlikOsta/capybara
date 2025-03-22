from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import AuthorProfileView, TelegramAuthView

app_name = 'user'

urlpatterns = [
    path('author/<int:author_id>/', AuthorProfileView.as_view(), name='author_profile'),
    path('auth/telegram/', TelegramAuthView.as_view(), name='telegram_auth'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
