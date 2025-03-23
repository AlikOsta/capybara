from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model

from .utils import verify_telegram_data, extract_telegram_user_data

User = get_user_model()


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
        
        # Проверяем, существует ли пользователь
        user, created = User.objects.update_or_create(
            telegram_id=telegram_id,
            defaults=telegram_user_data
        )
        
        # Генерируем токены JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.username,
                'first_name': user.first_name_tg,
                'last_name': user.last_name_tg,
                'photo_url': user.photo_url,
                'is_new': created
            }
        })
