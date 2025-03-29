import os
import logging
from asgiref.sync import sync_to_async
from django.conf import settings
from telegram import InputMediaPhoto
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes, CallbackContext
from app.models import Product, Category, City
from user_capybara.models import TelegramUser


logger = logging.getLogger(__name__)

@sync_to_async
def get_product_by_id(product_id: int) -> dict | None:
    """Асинхронно получает продукт по ID и возвращает словарь с данными."""
    try:
        product = Product.objects.select_related('category').get(id=product_id)
        image_url = f"https://capybarashop.store{product.image.url}" if product.image else None
        author = product.author.get_full_name()
        return {
            'id': product.id,
            'title': product.title,
            'price': product.price,
            'currency': product.currency,
            'description': product.description,
            'category_name': product.category.name,
            'author': author,
            'image_url': image_url, 

        }

    except Product.DoesNotExist:
        logger.error(f"Продукт с ID {product_id} не найден")
        return None
    

@sync_to_async
def get_info_count() -> dict | None:
    """Асинхронно получает продукт по ID и возвращает словарь с данными."""
    try:
        count_prod = Product.objects.count()
        count_cat = Category.objects.count()
        count_user = TelegramUser.objects.count()
        count_city = City.objects.count()

        return {
            'count_prod': count_prod,
            'count_cat': count_cat,
            'count_user': count_user,
            'count_city': count_city
        }

    except:
        return None

# @sync_to_async
# def get_or_create_user(telegram_id: int, username: str, first_name: str, last_name: str) -> TelegramUser | None:
#     """Создает или обновляет пользователя в базе данных."""
#     try:
#         user, _ = TelegramUser.objects.update_or_create(
#             telegram_id=telegram_id,
#             defaults={
#                 'username': username or '',
#                 'first_name': first_name or '',
#                 'last_name': last_name or '',
#                 'last_activity': timezone.now()
#             }
#         )
#         return user
#     except Exception as e:
#         logger.error(f"Ошибка при создании/обновлении пользователя: {e}", exc_info=True)
#         return None

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""

    user = update.effective_user
    args = context.args
    mini_app_url = "https://capybarashop.store/user/mini-app/"

    if args and args[0].startswith('product_'):
        try:
            product_id = int(args[0].split('_')[1])
            product_data = await get_product_by_id(product_id)

            if product_data:
                auth_url = f"https://capybarashop.store/user/mini-app/?product_id={product_id}"

                keyboard = [
                    [InlineKeyboardButton("Открыть объявление", web_app=WebAppInfo(url=auth_url))],
                    [InlineKeyboardButton("Все объявления", web_app=WebAppInfo(url=mini_app_url))]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                caption = (
                    f"<b>{product_data['title']}</b>\n\n"
                    f"🛒 Цена: {product_data['price']} {product_data['currency']}\n"
                    f"📂 Категория: {product_data['category_name']}\n\n"
                    f"📖 Описание: {product_data.get('description', 'Нет описания')}\n\n"
                    f"👤 Продавец - {product_data.get('author')}\n\n"
                )
                
                image_url = product_data.get("image_url")

                if image_url:
                    await update.message.reply_photo(photo=image_url, caption=caption, reply_markup=reply_markup, parse_mode='HTML')
                else:
                    await update.message.reply_html(caption, reply_markup=reply_markup)

            else:

                error__image_path = "https://i.ibb.co/W13Rtfc/error.png"
                keyboard = [
                    [InlineKeyboardButton("Все объявления", web_app=WebAppInfo(url=mini_app_url))]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                caption = (
                    f"❌ К сожалению, объявление не найдено или было удалено.\n\n"
                    "Вы можете просмотреть другие объявления, нажав на кнопку ниже:"
                )
                await update.message.reply_photo(photo=error__image_path, caption=caption, reply_markup=reply_markup, parse_mode='HTML')

        except ValueError:
            logger.error("Некорректный формат ID продукта")

            error__image_path = "https://i.ibb.co/W13Rtfc/error.png"
            keyboard = [
                    [InlineKeyboardButton("Все объявления", web_app=WebAppInfo(url=mini_app_url))]
                ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            caption = (
                    f"❌ <b>Некорректный формат ID продукта</b>\n\n"
                )

            await update.message.reply_photo(photo=error__image_path, caption=caption, reply_markup=reply_markup, parse_mode='HTML')
        return

    photo = "https://i.ibb.co/zWyhswRv/start.png"

    keyboard = [
        [InlineKeyboardButton("Открыть приложение", web_app=WebAppInfo(url=mini_app_url))],
        [InlineKeyboardButton("Помощь", callback_data="help"), InlineKeyboardButton("О нас", callback_data="info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"Привет, <b>{user.first_name}</b>! 👋\n\n"
        f"Добро пожаловать в Capybara Marketplace\n\n"
        f"Здесь вы можете покупать и продавать товары, "
        f"общаться с продавцами и находить лучшие предложения.\n\n"
        f"Нажмите кнопку ниже, чтобы открыть приложение:"
    )

    await update.message.reply_photo(photo=photo, caption=caption, reply_markup=reply_markup, parse_mode='HTML')


async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на inline-кнопки."""
    query = update.callback_query
    await query.answer()
   
    if query.data == "help":
        await help_handler(update, context)
    elif query.data == "info":
        await info_handler(update, context)
    elif query.data == "back_to_start":
        await back_to_start_callback(update, context)

async def back_to_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик для кнопки 'Назад'"""
    query = update.callback_query
    user = query.from_user
    
    photo = "https://i.ibb.co/zWyhswR/start.png" 
    
    keyboard = [
        [InlineKeyboardButton("Открыть приложение", web_app=WebAppInfo(url="https://capybarashop.store/user/mini-app/"))],
        [InlineKeyboardButton("Помощь", callback_data="help"), InlineKeyboardButton("О нас", callback_data="info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = (
        f"Привет, <b>{user.first_name}</b>! 👋\n\n"
        f"Добро пожаловать в Capybara Marketplace!\n\n"
        f"Здесь вы можете покупать и продавать товары, "
        f"общаться с продавцами и находить лучшие предложения.\n\n"
        f"Нажмите кнопку ниже, чтобы открыть приложение:"
    )
    
    await query.message.edit_caption(caption=caption, reply_markup=reply_markup, parse_mode='HTML')


async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_url: str, text: str) -> None:
    """Универсальный обработчик команд с поддержкой как прямых команд, так и callback-запросов."""
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_to_start")]])
    
    if update.callback_query:
        # Для callback-запросов редактируем существующее сообщение
        message = update.callback_query.message
        try:
            # Пробуем изменить медиа (фото + текст)
            await message.edit_caption(
                caption=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except Exception as e:
            # Если не получается, отправляем новое сообщение
            logger.error(f"Ошибка при редактировании сообщения: {e}")
            chat_id = message.chat_id
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
                caption=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    else:
        # Для прямых команд отправляем новое сообщение
        message = update.message
        await message.reply_photo(photo=photo_url, caption=text, reply_markup=reply_markup, parse_mode='HTML')


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    photo = "https://i.ibb.co/N27msW6y/help.png"
    text = (
        "🔍 <b>Справка по использованию Capybara</b>\n\n"
        "Для использования сервиса Capybara Marketplace вам не нужна регистрация или авторизация. Все, что вам нужно — это открыть приложение и наслаждаться покупками и продажами.\n"
        "Мы используем только официальные технологии Telegram и не храним никакой информации о вас.\n"
        "Мы применяем систему рейтингов для продавцов, поэтому вы можете не только сортировать товары по цене, но и обращать внимание на рейтинг продавцов, что сделает вашу покупку более безопасной.\n"
        "А самое главное — мы экономим ваше время на поиске товаров.\n\n"
        
        "Дополнительные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/info - Информация о сервисе\n\n"
        f"Если у вас возникли вопросы, напишите нам <a href='t.me/A43721'>Команда Capybara</a>"
    )
    
    await handle_command(update, context, photo, text)


async def info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /info."""
    photo = "https://i.ibb.co/ZpTx5g8b/info.png"
    data = await get_info_count()
    
    text = (
        f"<b>Расскажу немного про сервис Capybara Marketplace</b>\n\n"
        f"Capybara Marketplace — это современный маркетплейс, созданный для удобной покупки и продажи товаров через Telegram.\n"
        f"Больше не нужно искать товары в десятках различных групп и чатах — мы собрали все в одном месте.\n\n"
        
        f"👥 Уже более {data['count_user']} пользователей пользуются нашим сервисом.\n"
        f"📈 У нас более {data['count_prod']} объявлений в {data['count_cat']} различных категориях.\n"
        f"🏘 Мы работаем в {data['count_city']} городах Аргентины.\n\n"
        
        f"Мы стремимся предоставить удобный и безопасный сервис как для покупателей, так и для продавцов.\n"
        f"Цени свое время — используй его с пользой.\n\n"
        
        f"Если у вас возникли вопросы, напишите нам <a href='t.me/A43721'>Команда Capybara</a>"
    )
    
    await handle_command(update, context, photo, text)



async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений."""
    keyboard = [[InlineKeyboardButton("Открыть приложение", web_app=WebAppInfo(url=settings.TELEGRAM_MINI_APP_URL))]]
    await update.message.reply_text("Я понимаю только команды. Нажмите кнопку ниже, чтобы открыть приложение:", reply_markup=InlineKeyboardMarkup(keyboard))
