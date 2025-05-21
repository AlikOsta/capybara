import asyncio
import logging
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
import os

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    LabeledPrice,
    PreCheckoutQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
    WebAppInfo,
)
from aiogram.client.default import DefaultBotProperties
from app.models import Product, Category, City
from user_capybara.models import TelegramUser

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

prices = [LabeledPrice(label="Поддержать проект ⭐️", amount=100)]

START_PHOTO_URL = os.getenv("PHOTO_START")
ABOUT_PHOTO_URL = os.getenv("PHOTO_INFO")
HELP_PHOTO_URL = os.getenv("PHOTO_HELP")
DONATE_PHOTO_URL = os.getenv("PHOTO_DONATE")
THANKS_PHOTO_URL = os.getenv("PHOTO_THANKS")
ERROR_PHOTO_URL = os.getenv("PHOTO_ERROR")

URL = os.getenv("TELEGRAM_MINI_APP_URL")
BASE_URL = os.getenv("BASE_URL", "")
SAPPORT_URL = os.getenv("SUPPORT_URL")

@sync_to_async
def get_info_count() -> dict | None:
    """Асинхронно получает статистику и возвращает словарь с данными."""
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
    except Exception as e:
        logging.error(f"Error getting counts: {e}")
        return None

@sync_to_async
def get_product_by_id(product_id: int) -> dict | None:
    """Асинхронно получает продукт по ID и возвращает словарь с данными."""
    try:
        product = Product.objects.select_related('category').get(id=product_id)
        image_url = f"{BASE_URL}{product.image.url}" if product.image else None
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
        logging.error(f"Продукт с ID {product_id} не найден")
        return None
    except Exception as e:
        logging.error(f"Error getting product: {e}")
        return None

def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть мини-приложение",
            web_app=WebAppInfo(url=URL)
        )],
        [InlineKeyboardButton(text="О нас", callback_data="about"),
        InlineKeyboardButton(text="Помощь", callback_data="help")],
        [InlineKeyboardButton(text="Поддержать проект ⭐️", callback_data="pay")],
    ])

back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="back")]
])

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await bot.delete_webhook(drop_pending_updates=True)
    user = message.from_user
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if args and args[0].startswith('product_'):
        try:
            product_id = int(args[0].split('_')[1])
            product_data = await get_product_by_id(product_id)

            if product_data:
                auth_url = f"{URL}?product_id={product_id}"

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Открыть объявление", web_app=WebAppInfo(url=auth_url))],
                    [InlineKeyboardButton(text="Все объявления", web_app=WebAppInfo(url=URL))]
                ])

                caption = (
                    f"<b>{product_data['title']}</b>\n\n"
                    f"🛒 Цена: {product_data['price']} {product_data['currency']}\n"
                    f"📂 Категория: {product_data['category_name']}\n\n"
                    f"📖 Описание: {product_data.get('description', 'Нет описания')}\n\n"
                    f"👤 Продавец - {product_data.get('author')}\n\n"
                )
                
                image_url = product_data.get("image_url")

                if image_url:
                    await message.answer_photo(photo=image_url, caption=caption, reply_markup=keyboard)
                else:
                    await message.answer(caption, reply_markup=keyboard)
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Все объявления", web_app=WebAppInfo(url=URL))]
                ])

                caption = (
                    f"❌ К сожалению, объявление не найдено или было удалено.\n\n"
                    "Вы можете просмотреть другие объявления, нажав на кнопку ниже:"
                )
                await message.answer_photo(photo=ERROR_PHOTO_URL, caption=caption, reply_markup=keyboard)

        except ValueError:
            logging.error("Некорректный формат ID продукта")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Все объявления", web_app=WebAppInfo(url=URL))]
            ])
            caption = f"❌ <b>Некорректный формат ID продукта</b>\n\n"
            await message.answer_photo(photo=ERROR_PHOTO_URL, caption=caption, reply_markup=keyboard)
        return

    await message.answer_photo(
        photo=START_PHOTO_URL,
        caption=(
            f"Привет, <b>{user.first_name}</b>! 👋\n\n"
            f"Добро пожаловать в Capybara Marketplace\n\n"
            f"Здесь вы можете покупать и продавать товары, "
            f"общаться с продавцами и находить лучшие предложения.\n\n"
            f"Нажмите кнопку ниже, чтобы открыть приложение:"
        ),
        reply_markup=start_keyboard()
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer_photo(
        photo=HELP_PHOTO_URL,
        caption=(
            "🔍 <b>Справка по использованию Capybara</b>\n\n"
            "Для использования сервиса Capybara Marketplace вам не нужна регистрация или авторизация. Все, что вам нужно — это открыть приложение и наслаждаться покупками и продажами.\n"
            "Мы используем только официальные технологии Telegram и не храним никакой информации о вас.\n"
            "Мы применяем систему рейтингов для продавцов, поэтому вы можете не только сортировать товары по цене, но и обращать внимание на рейтинг продавцов, что сделает вашу покупку более безопасной.\n"
            "А самое главное — мы экономим ваше время на поиске товаров.\n\n"
            
            "Дополнительные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать эту справку\n"
            "/info - Информация о сервисе\n\n"
            f"Если у вас возникли вопросы, напишите нам <a href='{SAPPORT_URL}'>Команда Capybara</a>"
        ),
        reply_markup=back_kb
    )

@dp.message(Command("info"))
async def cmd_info(message: types.Message):
    data = await get_info_count() or {'count_prod': 'XXX', 'count_cat': 'XXX', 'count_user': 'XXX', 'count_city': 'XXX'}
    
    await message.answer_photo(
        photo=ABOUT_PHOTO_URL,
        caption=(
            f"<b>Расскажу немного про сервис Capybara Marketplace</b>\n\n"
            f"Capybara Marketplace — это современный маркетплейс, созданный для удобной покупки и продажи товаров через Telegram.\n"
            f"Больше не нужно искать товары в десятках различных групп и чатах — мы собрали все в одном месте.\n\n"
            
            f"👥 Уже более {data['count_user']} пользователей пользуются нашим сервисом.\n"
            f"📈 У нас более {data['count_prod']} объявлений в {data['count_cat']} различных категориях.\n"
            f"🏘 Мы работаем в {data['count_city']} городах Аргентины.\n\n"
            
            f"Мы стремимся предоставить удобный и безопасный сервис как для покупателей, так и для продавцов.\n"
            f"Цени свое время — используй его с пользой.\n\n"
            
            f"Если у вас возникли вопросы, напишите нам <a href='{SAPPORT_URL}'>Команда Capybara</a>"
        ),
        reply_markup=back_kb
    )

@dp.callback_query(F.data == "about")
async def callback_about(query: types.CallbackQuery):
    data = await get_info_count() or {'count_prod': 'XXX', 'count_cat': 'XXX', 'count_user': 'XXX', 'count_city': 'XXX'}
    
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=ABOUT_PHOTO_URL,
            caption=(
                f"<b>Расскажу немного про сервис Capybara Marketplace</b>\n\n"
                f"Capybara Marketplace — это современный маркетплейс, созданный для удобной покупки и продажи товаров через Telegram.\n"
                f"Больше не нужно искать товары в десятках различных групп и чатах — мы собрали все в одном месте.\n\n"
                
                f"👥 Уже более {data['count_user']} пользователей пользуются нашим сервисом.\n"
                f"📈 У нас более {data['count_prod']} объявлений в {data['count_cat']} различных категориях.\n"
                f"🏘 Мы работаем в {data['count_city']} городах Аргентины.\n\n"
                
                f"Мы стремимся предоставить удобный и безопасный сервис как для покупателей, так и для продавцов.\n"
                f"Цени свое время — используй его с пользой.\n\n"
                
                f"Если у вас возникли вопросы, напишите нам <a href='{SAPPORT_URL}'>Команда Capybara</a>"
            )
        ),
        reply_markup=back_kb
    )
    await query.answer()

@dp.callback_query(F.data == "help")
async def callback_help(query: types.CallbackQuery):
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=HELP_PHOTO_URL,
            caption=(
                "🔍 <b>Справка по использованию Capybara</b>\n\n"
                "Для использования сервиса Capybara Marketplace вам не нужна регистрация или авторизация. Все, что вам нужно — это открыть приложение и наслаждаться покупками и продажами.\n"
                "Мы используем только официальные технологии Telegram и не храним никакой информации о вас.\n"
                "Мы применяем систему рейтингов для продавцов, поэтому вы можете не только сортировать товары по цене, но и обращать внимание на рейтинг продавцов, что сделает вашу покупку более безопасной.\n"
                "А самое главное — мы экономим ваше время на поиске товаров.\n\n"
                
                "Дополнительные команды:\n"
                "/start - Начать работу с ботом\n"
                "/help - Показать эту справку\n"
                "/info - Информация о сервисе\n\n"
                f"Если у вас возникли вопросы, напишите нам <a href='{SAPPORT_URL}'>Команда Capybara</a>"
            )
        ),
        reply_markup=back_kb
    )
    await query.answer()

@dp.callback_query(F.data == "pay")
async def callback_pay(query: types.CallbackQuery):
    await bot.send_invoice(
        chat_id=query.message.chat.id,
        title="Донат проекту",
        description="Все собранные средства пойдут на развитие проекта. Спасибо за Ваше доверие!",
        payload="donate_payload",
        provider_token=os.getenv("PAYMENT_PROVIDER_TOKEN", ""),  
        currency="XTR",
        prices=prices,
    )
    await query.answer()


@dp.pre_checkout_query(F.invoice_payload == "donate_payload")
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    total = message.successful_payment.total_amount / 100
    await message.answer_photo(
        photo=THANKS_PHOTO_URL,
        caption=f"Спасибо за донат ⭐️ {total:.2f} XTR! Ваша поддержка бесценна.",
        reply_markup=back_kb
    )


@dp.callback_query(F.data == "back")
async def callback_back(query: types.CallbackQuery):
    user = query.from_user
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=START_PHOTO_URL,
            caption=(
                f"Привет, <b>{user.first_name}</b>! 👋\n\n"
                f"Добро пожаловать в Capybara Marketplace\n\n"
                f"Здесь вы можете покупать и продавать товары, "
                f"общаться с продавцами и находить лучшие предложения.\n\n"
                f"Нажмите кнопку ниже, чтобы открыть приложение:"
            )
        ),
        reply_markup=start_keyboard()
    )
    await query.answer()


@dp.message()
async def handle_all_messages(message: types.Message):
    """Обработчик для всех остальных сообщений"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть приложение", web_app=WebAppInfo(url=URL))]
    ])
    await message.answer("Я понимаю только команды. Нажмите кнопку ниже, чтобы открыть приложение:", 
                         reply_markup=keyboard)


async def main():
    """Основная функция запуска бота"""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Удаляем вебхук перед запуском поллинга
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

