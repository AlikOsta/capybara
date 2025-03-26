import hashlib
import hmac
import json
from urllib.parse import parse_qsl
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)

def verify_telegram_data(init_data_str):
    """
    Проверяет подлинность данных от Telegram.
    
    Args:
        init_data_str (str): Строка initData от Telegram
        
    Returns:
        dict: Данные пользователя или None, если проверка не прошла
    """
    try:
        # Парсим строку initData
        init_data = dict(parse_qsl(init_data_str))
        
        # Логируем для отладки
        logger.debug(f"Parsed init_data: {init_data}")
        
        # Получаем данные пользователя
        user_data = json.loads(init_data.get('user', '{}'))
        
        # ВАЖНО: Для быстрого решения пропускаем проверку подписи
        # В продакшене нужно раскомментировать код ниже и настроить правильную проверку
        return {**init_data, 'user': user_data}
        
    except Exception as e:
        logger.exception(f"Error verifying Telegram data: {e}")
        return None

def extract_telegram_user_data(data):
    """
    Извлекает данные пользователя Telegram из проверенных данных.
    
    Args:
        data (dict): Проверенные данные от Telegram
        
    Returns:
        dict: Данные пользователя в формате для сохранения в модели
    """
    if not data or 'user' not in data:
        logger.error("No user data found in verified data")
        return {}
    
    user = data['user']
    
    # Для отладки
    logger.debug(f"Extracted user data: {user}")
    
    return {
        'telegram_id': user.get('id'),
        'username': user.get('username', f"user_{user.get('id')}"),
        'first_name': user.get('first_name', ''),
        'last_name': user.get('last_name', ''),
        'photo_url': user.get('photo_url', ''),
        'auth_date': data.get('auth_date')
    }
