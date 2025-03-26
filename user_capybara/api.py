from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model, login
import logging

from .utils import verify_telegram_data, extract_telegram_user_data

User = get_user_model()
logger = logging.getLogger(__name__)

class TelegramAuthView(APIView):
    """
    API-представление для аутентификации пользователей через Telegram Mini App.
    """
    permission_classes = []  # Разрешаем доступ без аутентификации
    
    def post(self, request):
        # Получаем данные инициализации от Telegram
        init_data = request.data.get('initData')
        
        if not init_data:
            return Response(
                {'error': 'Отсутствуют данные инициализации Telegram'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем подлинность данных
        user_data = verify_telegram_data(init_data)
        if not user_data:
            return Response(
                {'error': 'Недействительные данные Telegram'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Извлекаем данные пользователя
        telegram_user_data = extract_telegram_user_data(user_data)
        telegram_id = telegram_user_data.get('telegram_id')
        
        if not telegram_id:
            return Response(
                {'error': 'Отсутствует Telegram ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Проверяем, существует ли пользователь
            user, created = User.objects.update_or_create(
                telegram_id=telegram_id,
                defaults=telegram_user_data
            )
            
            # Авторизуем пользователя в текущей сессии
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            # Генерируем токены JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Создаем ответ
            response = Response({
                'refresh': str(refresh),
                'access': access_token,
                'user': {
                    'id': user.id,
                    'telegram_id': user.telegram_id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'photo_url': user.photo_url,
                }
            })
            
            # Устанавливаем токен в cookie
            response.set_cookie(
                key='jwt_access',
                value=access_token,
                httponly=True,
                samesite='Lax',
                secure=request.is_secure(),
                max_age=3600 * 24
            )
            
            return response
            
        except Exception as e:
            logger.exception(f"Error during user creation/update: {e}")
            return Response(
                {'error': 'Ошибка при создании/обновлении пользователя'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    """
    Проверяет авторизацию пользователя.
    """
    return Response({
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'photo_url': getattr(request.user, 'photo_url', None),
        }
    })
