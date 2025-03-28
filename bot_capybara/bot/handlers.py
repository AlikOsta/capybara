import logging
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from app.models import Product
from user_capybara.models import TelegramUser

logger = logging.getLogger(__name__)

@sync_to_async
def get_product_by_id(product_id):
    """
    Асинхронно получает продукт по ID и возвращает словарь с данными.
    """
    try:
        logger.info(f"Поиск продукта с ID {product_id}")
        # Добавляем логирование для отладки
        all_products = list(Product.objects.all().values('id', 'title'))
        logger.info(f"Все товары в базе: {all_products}")
        
        product = Product.objects.filter(id=product_id).first()
        if product:
            logger.info(f"Продукт найден: {product.title}, статус: {product.status}")
            # Возвращаем словарь с данными продукта
            return {
                'id': product.id,
                'title': product.title,
                'price': str(product.price),
                'currency': str(product.currency),
                'category_name': product.category.name
            }
        else:
            logger.warning(f"Продукт с ID {product_id} не найден")
            return None
    except Exception as e:
        logger.error(f"Ошибка при получении продукта: {e}", exc_info=True)
        return None
    

@sync_to_async
def get_or_create_user(telegram_id, username, first_name, last_name):
    """
    Создает или обновляет пользователя в базе данных.
    """
    try:
        user, created = TelegramUser.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': username or '',
                'first_name': first_name or '',
                'last_name': last_name or '',
                'last_activity': timezone.now()
            }
        )
        return user
    except Exception as e:
        logger.error(f"Ошибка при создании/обновлении пользователя: {e}")
        return None

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    try:
        user = update.effective_user
        args = context.args
        
        logger.info(f"Пользователь {user.id} ({user.username}) вызвал команду /start с аргументами: {args}")

        if args and args[0].startswith('product_'):

            try:
                product_id = int(args[0].split('_')[1])
                logger.info(f"Запрошен продукт с ID {product_id}")
                
                product_data = await get_product_by_id(product_id)
                
                if product_data:
                    logger.info(f"Продукт найден: {product_data['title']}")
                    
                    base_url = "https://capybarashop.store"

                    mini_app_url = settings.TELEGRAM_MINI_APP_URL

                    auth_url = f"{base_url}/user/mini-app/?product_id={product_id}"

                    keyboard = [
                        [InlineKeyboardButton("Открыть объявление", web_app=WebAppInfo(url=auth_url))],
                        [InlineKeyboardButton("Все объявления", web_app=WebAppInfo(url=mini_app_url))]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_html(
                        f"<b>{product_data['title']}</b>\n\n"
                        f"Цена: {product_data['price']} {product_data['currency']}\n"
                        f"Категория: {product_data['category_name']}\n\n"
                        f"Нажмите кнопку ниже, чтобы открыть объявление:",
                        reply_markup=reply_markup
                    )
                else:
                    logger.warning(f"Продукт с ID {product_id} не найден")
                    await update.message.reply_text(
                        "Объявление не найдено или было удалено."
                    )
            except ValueError as e:
                logger.error(f"Ошибка при парсинге ID продукта: {e}")
                await update.message.reply_text(
                    "Некорректный формат ссылки на объявление."
                )
            except Exception as e:
                logger.error(f"Ошибка при обработке deep link: {e}", exc_info=True)
                await update.message.reply_text(
                    "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже."
                )
        else:
            # Стандартное приветствие
            keyboard = [
                [InlineKeyboardButton("Открыть приложение", web_app=WebAppInfo(url=settings.TELEGRAM_MINI_APP_URL))]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(
                f"Привет, <b>{user.first_name}</b>! 👋\n\n"
                f"Я бот маркетплейса Capybara. Здесь вы можете покупать и продавать товары.\n\n"
                f"Нажмите кнопку ниже, чтобы открыть приложение:",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Необработанная ошибка в start_handler: {e}", exc_info=True)
        await update.message.reply_text(
            "Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже."
        )




async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    keyboard = [
        [InlineKeyboardButton("Открыть приложение", web_app=WebAppInfo(url=settings.TELEGRAM_MINI_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Capybara - это маркетплейс, где вы можете покупать и продавать товары.\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать справку\n"
        "/open - Открыть приложение\n\n"
        "Нажмите кнопку ниже, чтобы открыть приложение:",
        reply_markup=reply_markup
    )

async def open_app_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /open."""
    keyboard = [
        [InlineKeyboardButton("Открыть приложение", web_app=WebAppInfo(url=settings.TELEGRAM_MINI_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Нажмите кнопку ниже, чтобы открыть приложение:",
        reply_markup=reply_markup
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений."""
    keyboard = [
        [InlineKeyboardButton("Открыть приложение", web_app=WebAppInfo(url=settings.TELEGRAM_MINI_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Я понимаю только команды. Нажмите кнопку ниже, чтобы открыть приложение:",
        reply_markup=reply_markup
    )
