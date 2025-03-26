"""
Модуль с обработчиками команд и сообщений Telegram бота.
"""
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from django.conf import settings
from user_capybara.models import TelegramUser
from app.models import Product
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

# Асинхронные функции для работы с базой данных
@sync_to_async
def update_or_create_telegram_user(telegram_id, username, first_name, last_name):
    """
    Асинхронно создает или обновляет пользователя Telegram в базе данных.
    
    Args:
        telegram_id (int): ID пользователя в Telegram
        username (str): Имя пользователя в Telegram
        first_name (str): Имя пользователя
        last_name (str): Фамилия пользователя
        
    Returns:
        tuple: (user, created) - созданный/обновленный пользователь и флаг создания
    """
    try:
        return TelegramUser.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': username or f"user_{telegram_id}",
                'first_name': first_name,
                'last_name': last_name,
            }
        )
    except Exception as e:
        logger.error(f"Ошибка при создании/обновлении пользователя: {e}")
        raise

@sync_to_async
def get_product_by_id(product_id):
    """
    Асинхронно получает продукт по ID.
    
    Args:
        product_id (int): ID продукта
        
    Returns:
        Product: объект продукта или None, если продукт не найден
    """
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        logger.warning(f"Продукт с ID {product_id} не найден")
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении продукта: {e}")
        return None

# Создание кнопки для открытия Mini App
def get_webapp_button(url=None):
    """
    Создает кнопку для открытия Mini App.
    
    Args:
        url (str, optional): URL для открытия. По умолчанию используется основной URL приложения.
        
    Returns:
        InlineKeyboardMarkup: разметка с кнопкой
    """
    app_url = 'https://capybarashop.store/user/mini-app/'
    keyboard = [
        [InlineKeyboardButton(
            "Открыть Capybara", 
            web_app=WebAppInfo(url=app_url)
        )]
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработчики команд
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start.
    
    Регистрирует пользователя и отправляет приветственное сообщение.
    Если команда содержит параметр product_id, показывает информацию о продукте.
    
    Args:
        update (Update): объект обновления Telegram
        context (ContextTypes.DEFAULT_TYPE): контекст обработчика
        
    Returns:
        None
    """
    user = update.effective_user
    
    try:
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
            except (ValueError, IndexError) as e:
                logger.warning(f"Неверный формат параметра product_id: {e}")
                await update.message.reply_text(
                    "Неверная ссылка на объявление."
                )
                # Продолжаем выполнение, чтобы показать стандартное приветствие
        
        # Отправляем приветственное сообщение с кнопкой
        reply_markup = get_webapp_button()
        await update.message.reply_html(
            f"Привет, {user.mention_html()}! 👋\n\n"
            f"Добро пожаловать в Capybara - платформу для размещения объявлений.\n\n"
            f"Нажмите на кнопку ниже, чтобы открыть приложение:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка в обработчике start: {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже."
        )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /help.
    
    Отправляет справочную информацию о боте.
    
    Args:
        update (Update): объект обновления Telegram
        context (ContextTypes.DEFAULT_TYPE): контекст обработчика
        
    Returns:
        None
    """
    try:
        reply_markup = get_webapp_button()
        
        await update.message.reply_text(
            "Это бот для доступа к платформе объявлений Capybara.\n\n"
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать эту справку\n"
            "/open - Открыть приложение\n\n"
            "Или просто нажмите на кнопку ниже:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка в обработчике help: {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже."
        )

async def open_app_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /open.
    
    Отправляет кнопку для открытия приложения.
    
    Args:
        update (Update): объект обновления Telegram
        context (ContextTypes.DEFAULT_TYPE): контекст обработчика
        
    Returns:
        None
    """
    try:
        reply_markup = get_webapp_button()
        
        await update.message.reply_text(
            "Нажмите на кнопку, чтобы открыть приложение:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка в обработчике open_app: {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже."
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик всех остальных сообщений.
    
    Проверяет, содержит ли сообщение ссылку на продукт, и обрабатывает соответственно.
    
    Args:
        update (Update): объект обновления Telegram
        context (ContextTypes.DEFAULT_TYPE): контекст обработчика
        
    Returns:
        None
    """
    try:
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
        reply_markup = get_webapp_button()
        
        await update.message.reply_text(
            "Я понимаю только команды /start, /help и /open.\n"
            "Или вы можете открыть приложение, нажав на кнопку ниже:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка в обработчике message: {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке сообщения. Пожалуйста, попробуйте позже."
        )
