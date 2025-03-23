from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import AuthorProfileView, TelegramAuthView
from .api import TelegramAuthView as TelegramAuthAPIView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'user'

urlpatterns = [
    path('author/<int:author_id>/', AuthorProfileView.as_view(), name='author_profile'),
    path('auth/telegram/', TelegramAuthView.as_view(), name='telegram_auth'),
    # API endpoints
    path('api/auth/telegram/', TelegramAuthAPIView.as_view(), name='telegram_auth_api'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
