from django.apps import AppConfig


class BotCapybaraConfig(AppConfig):
    """
    Конфигурация приложения Telegram бота Capybara.
    
    Это приложение отвечает за взаимодействие с Telegram API
    и обработку команд пользователей в Telegram боте.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot_capybara'
    verbose_name = 'Telegram Бот'
    
