from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import AuthorProfileView, TelegramAuthView, MiniAppView, UserProfileEditView
from .api import TelegramAuthView as TelegramAuthAPIView, check_auth


app_name = 'user'

urlpatterns = [
    path('author/<int:author_id>/', AuthorProfileView.as_view(), name='author_profile'),
    path('profile/edit/', UserProfileEditView.as_view(), name='profile_edit'),
    path('auth/telegram/', TelegramAuthView.as_view(), name='telegram_auth'),
    path('api/auth/telegram/', TelegramAuthAPIView.as_view(), name='telegram_auth_api'),
    path('mini-app/', MiniAppView.as_view(), name='mini_app'), 
        # JWT Token endpoints
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/auth/check/', check_auth, name='check_auth'),
]
