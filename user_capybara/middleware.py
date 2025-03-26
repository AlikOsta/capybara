import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

def get_user_from_jwt(request):
    """
    Получает пользователя из JWT-токена в заголовке Authorization или в cookies.
    """
    # Проверяем, есть ли уже аутентифицированный пользователь
    if hasattr(request, '_cached_user'):
        return request._cached_user
    
    # Пытаемся получить токен из заголовка
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    token = None
    
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    else:
        # Если токена нет в заголовке, проверяем cookies
        token = request.COOKIES.get('jwt_access')
    
    if not token:
        return None
    
    try:
        # Проверяем токен
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        
        # Кэшируем пользователя
        request._cached_user = user
        return user
    except Exception:
        return None


class JWTAuthenticationMiddleware:
    """
    Middleware для аутентификации пользователей с помощью JWT-токенов.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Если пользователь не аутентифицирован через сессию,
        # пытаемся аутентифицировать через JWT
        if not request.user.is_authenticated:
            request.user = SimpleLazyObject(lambda: get_user_from_jwt(request) or request.user)
        
        response = self.get_response(request)
        return response
