"""
Django management команда для запуска Telegram бота.
"""
import logging
from django.core.management.base import BaseCommand
from bot_capybara.bot import start_bot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Django management команда для запуска Telegram бота.
    """
    help = 'Запускает Telegram бота'

    def handle(self, *args, **options):
        """
        Метод, который вызывается при выполнении команды.
        """
        self.stdout.write(self.style.SUCCESS('Запуск Telegram бота...'))
        try:
            start_bot()
            return 0
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при запуске бота: {e}'))
            return 1
