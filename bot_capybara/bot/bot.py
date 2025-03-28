"""
Модуль для инициализации и запуска Telegram бота.
"""
import logging
import sys
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from django.conf import settings
from .handlers import start_handler, help_handler, message_handler, info_handler, button_callback_handler

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capybara.settings')
django.setup()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

def start_bot():
    """
    Запускает Telegram бота.
    
    Функция проверяет наличие токена, создает приложение,
    регистрирует обработчики команд и запускает бота.
    
    Returns:
        None
    """
    # Проверяем наличие токена
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не найден в настройках!")
        return
    
    try:
        logger.info("Запуск бота...")
        
        # Создаем приложение
        application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(CommandHandler("help", help_handler))
        application.add_handler(CommandHandler("info", info_handler))
        
        # Обработчик для всех остальных сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        application.add_handler(CallbackQueryHandler(button_callback_handler))
        
        # Запускаем бота
        application.run_polling()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
