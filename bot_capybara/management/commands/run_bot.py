from django.core.management.base import BaseCommand
from bot_capybara.bot.bot import start_bot

class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Запуск Telegram бота...'))
        start_bot()
