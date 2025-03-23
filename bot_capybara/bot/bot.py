import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from django.conf import settings
from .handlers import start_handler, help_handler, open_app_handler, message_handler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start_bot():
    """
    Запускает Telegram бота.
    """
    # Проверяем наличие токена
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не найден в настройках!")
        return
    
    logger.info("Запуск бота...")
    
    # Создаем приложение
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("open", open_app_handler))
    
    # Обработчик для всех остальных сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Запускаем бота
    logger.info(f"Бот @{settings.TELEGRAM_BOT_USERNAME} запущен")
    application.run_polling()
