from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from django.conf import settings
from user_capybara.models import TelegramUser
from app.models import Product
from asgiref.sync import sync_to_async
import re

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

# Асинхронная функция для получения продукта по ID
@sync_to_async
def get_product_by_id(product_id):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None

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
    
    # Проверяем, есть ли параметры в команде /start
    args = context.args
    
    if args and args[0].startswith('product_'):
        # Извлекаем ID продукта
        try:
            product_id = int(args[0].split('_')[1])
            product = await get_product_by_id(product_id)
            
            if product:
                # Создаем кнопку для открытия Mini App с этим продуктом
                product_url = f"{settings.TELEGRAM_MINI_APP_URL}product/{product_id}/"
                keyboard = [
                    [InlineKeyboardButton(
                        "Открыть объявление", 
                        web_app=WebAppInfo(url=product_url)
                    )]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Отправляем информацию о продукте
                await update.message.reply_html(
                    f"<b>{product.title}</b>\n\n"
                    f"Цена: {product.price} {product.currency}\n"
                    f"Категория: {product.category.name}\n\n"
                    f"Нажмите на кнопку ниже, чтобы открыть объявление:",
                    reply_markup=reply_markup
                )
                return
            else:
                await update.message.reply_text(
                    "Объявление не найдено или было удалено."
                )
                # Продолжаем выполнение, чтобы показать стандартное приветствие
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Неверная ссылка на объявление."
            )
            # Продолжаем выполнение, чтобы показать стандартное приветствие
    
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
    message_text = update.message.text
    
    # Проверяем, содержит ли сообщение ссылку на продукт
    product_link_pattern = r'https://t\.me/CapybaraMPRobot\?start=product_(\d+)'
    match = re.search(product_link_pattern, message_text)
    
    if match:
        product_id = int(match.group(1))
        product = await get_product_by_id(product_id)
        
        if product:
            # Создаем кнопку для открытия Mini App с этим продуктом
            product_url = f"{settings.TELEGRAM_MINI_APP_URL}product/{product_id}/"
            keyboard = [
                [InlineKeyboardButton(
                    "Открыть объявление", 
                    web_app=WebAppInfo(url=product_url)
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Отправляем информацию о продукте
            await update.message.reply_html(
                f"<b>{product.title}</b>\n\n"
                f"Цена: {product.price} {product.currency}\n"
                f"Категория: {product.category.name}\n\n"
                f"Нажмите на кнопку ниже, чтобы открыть объявление:",
                reply_markup=reply_markup
            )
            return
    
    # Стандартный ответ для других сообщений
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
