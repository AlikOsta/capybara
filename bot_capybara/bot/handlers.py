from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from django.conf import settings
from user_capybara.models import TelegramUser
from asgiref.sync import sync_to_async

# Создаем асинхронную версию update_or_create
@sync_to_async
def update_or_create_telegram_user(telegram_id, username, first_name, last_name):
    return TelegramUser.objects.update_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
        }
    )

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Используем асинхронную версию update_or_create
    telegram_user, created = await update_or_create_telegram_user(
        user.id, 
        user.username, 
        user.first_name, 
        user.last_name
    )
    
    # Создаем кнопку для открытия Mini App
    keyboard = [
        [InlineKeyboardButton(
            "Открыть Capybara", 
            web_app=WebAppInfo(url=settings.TELEGRAM_MINI_APP_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем приветственное сообщение с кнопкой
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! 👋\n\n"
        f"Добро пожаловать в Capybara - платформу для размещения объявлений.\n\n"
        f"Нажмите на кнопку ниже, чтобы открыть приложение:",
        reply_markup=reply_markup
    )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    # Создаем кнопку для открытия Mini App
    keyboard = [
        [InlineKeyboardButton(
            "Открыть Capybara", 
            web_app=WebAppInfo(url=settings.TELEGRAM_MINI_APP_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Это бот для доступа к платформе объявлений Capybara.\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/open - Открыть приложение\n\n"
        "Или просто нажмите на кнопку ниже:",
        reply_markup=reply_markup
    )

async def open_app_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /open"""
    # Создаем кнопку для открытия Mini App
    keyboard = [
        [InlineKeyboardButton(
            "Открыть Capybara", 
            web_app=WebAppInfo(url=settings.TELEGRAM_MINI_APP_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Нажмите на кнопку, чтобы открыть приложение:",
        reply_markup=reply_markup
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик всех остальных сообщений"""
    # Создаем кнопку для открытия Mini App
    keyboard = [
        [InlineKeyboardButton(
            "Открыть Capybara", 
            web_app=WebAppInfo(url=settings.TELEGRAM_MINI_APP_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Я понимаю только команды /start, /help и /open.\n"
        "Или вы можете открыть приложение, нажав на кнопку ниже:",
        reply_markup=reply_markup
    )
