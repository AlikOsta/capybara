"""
Скрипт для запуска Telegram бота.

Этот скрипт настраивает Django окружение и запускает Telegram бота.
Может быть запущен как отдельный процесс.
"""
import os
import sys
import django
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def setup_django():
    """
    Настраивает Django окружение для запуска бота вне Django сервера.
    
    Returns:
        bool: True, если настройка прошла успешно, иначе False
    """
    try:
        # Получаем путь к корневой директории проекта
        BASE_DIR = Path(__file__).resolve().parent.parent
        
        # Добавляем корневую директорию в sys.path
        sys.path.append(str(BASE_DIR))
        
        # Устанавливаем переменную окружения для настроек Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capybara.settings')
        
        # Настраиваем Django
        django.setup()
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при настройке Django: {e}")
        return False

def main():
    """
    Основная функция для запуска бота.
    
    Returns:
        int: 0 в случае успеха, 1 в случае ошибки
    """
    # Настраиваем Django
    if not setup_django():
        return 1
    
    try:
        # Импортируем функцию запуска бота после настройки Django
        from bot_capybara.bot import start_bot
        
        # Запускаем бота
        start_bot()
        
        return 0
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
