import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl
from django.conf import settings



def verify_telegram_data(init_data):
    """
    Проверяет подлинность данных, полученных от Telegram Mini App.
    
    Args:
        init_data (str): Строка с данными инициализации от Telegram WebApp
        
    Returns:
        dict: Словарь с данными пользователя, если проверка прошла успешно
        None: Если проверка не прошла
    """
    # Разбираем строку init_data на параметры
    data_dict = dict(parse_qsl(init_data))
    
    # Получаем хеш из данных
    received_hash = data_dict.pop('hash', None)
    if not received_hash:
        return None
    
    # Создаем отсортированную строку для проверки
    data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(data_dict.items())])
    
    # Создаем секретный ключ из токена бота
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    
    # Вычисляем хеш
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Сравниваем хеши
    if calculated_hash != received_hash:
        return None
    
    # Проверяем, не устарели ли данные (опционально)
    auth_date = int(data_dict.get('auth_date', 0))
    if time.time() - auth_date > 86400:  # 24 часа
        return None
    
    # Извлекаем и декодируем данные пользователя
    user_data = json.loads(data_dict.get('user', '{}'))
    
    # Добавляем auth_date к данным пользователя
    user_data['auth_date'] = int(data_dict.get('auth_date', 0))
    
    return user_data


def extract_telegram_user_data(user_data):
    """
    Извлекает необходимые данные пользователя из данных Telegram.
    
    Args:
        user_data (dict): Словарь с данными пользователя от Telegram
        
    Returns:
        dict: Словарь с данными для создания/обновления пользователя
    """
    return {
        'telegram_id': user_data.get('id'),
        'username': user_data.get('username'),
        'first_name_tg': user_data.get('first_name'),
        'last_name_tg': user_data.get('last_name'),
        'photo_url': user_data.get('photo_url'),
        'auth_date': user_data.get('auth_date')
    }
