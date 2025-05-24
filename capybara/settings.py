"""
Django settings for capybara project.
"""

from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta

# Загрузка переменных окружения из .env файла
load_dotenv()

# Базовые настройки
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []

# Приложения
DJANGO_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'django_q',
    'corsheaders',
    'django_filters', 
    'drf_yasg',
    'debug_toolbar',
    'imagekit',
]

LOCAL_APPS = [
    'app',
    'user_capybara',
    'bot_capybara',
    'stats',
    'api',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'user_capybara.middleware.JWTAuthenticationMiddleware',  
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# URL и шаблоны
ROOT_URLCONF = 'capybara.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.favorites_processor',
                'user_capybara.context_processors.telegram_user',  
            ],
        },
    },
]

WSGI_APPLICATION = 'capybara.wsgi.application'

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Интернационализация
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'ru-ru')
TIME_ZONE = os.getenv('TIME_ZONE', 'Europe/Moscow')
USE_I18N = True
USE_TZ = True

# Статические файлы и медиа
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Настройки по умолчанию
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'user_capybara.TelegramUser'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT настройки
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS настройки
CORS_ALLOWED_ORIGINS = [
    "https://web.telegram.org",
]
CORS_ALLOW_CREDENTIALS = True

# Настройки для Telegram бота
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME')
TELEGRAM_MINI_APP_URL = os.getenv('TELEGRAM_MINI_APP_URL')
BASE_URL = os.getenv('BASE_URL')

# Mistral API
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") 

# Django Q настройки
Q_CLUSTER = {
    'name': 'capybara',
    'workers': 4,
    'timeout': 60,
    'django_redis': None,
    'save_limit': 250,
    'retry': 500,
    'catch_up': False,
    'orm': 'default',
}

# CORS настройки
CORS_ALLOWED_ORIGINS = [
    "https://web.telegram.org",
    "https://capybarashop.store",
]
CORS_ALLOW_CREDENTIALS = True

# Настройки сессий
SESSION_COOKIE_SECURE = not DEBUG  # True в продакшене
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 дней

# Время кэширования в секундах
CACHE_MIDDLEWARE_SECONDS = 60 * 15  # 15 минут

# Настройки Jazzmin
JAZZMIN_SETTINGS = {
    # Заголовок
    "site_title": "Capybara Admin",
    "site_header": "Capybara",
    "site_brand": "Capybara",
    
    # Цвета и тема
    "site_logo": "images/logo.png",  # Логотип (если есть)
    "welcome_sign": "Добро пожаловать в админ-панель Capybara",
    "copyright": "Capybara © 2023",
    
    # Верхнее меню (опционально)
    "topmenu_links": [
        {"name": "Главная", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Сайт", "url": "/", "new_window": True},
    ],
    
    # Боковое меню
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # Пользовательские ссылки в боковом меню
    "custom_links": {
        "app": [
            {
                "name": "Статистика", 
                "url": "/admin/stats/dashboard/",  # Новый URL для объединенной статистики
                "icon": "fas fa-chart-line"
            },
        ]
    },
    
    # Иконки для приложений
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "app.product": "fas fa-shopping-cart",
        "app.category": "fas fa-list",
        "app.favorite": "fas fa-heart",
        "app.productview": "fas fa-eye",
    },
    
    # Настройка дашборда
    "dashboard_charts": True,  # Включаем графики на дашборде
    "changeform_format": "horizontal_tabs",
    "show_ui_builder": True,  # Включаем UI Builder для настройки
}

# Настройки UI для Jazzmin
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

JAZZMIN_SETTINGS.update({
    # Настройка дашборда
    "dashboard_charts": True,
    "dashboard_widgets": [
        {
            "name": "Статистика",
            "url": "stats:dashboard_stats",  
            "icon": "fas fa-chart-line",
            "description": "Общая статистика платформы",
        },
    ],
})

# Пути к изображениям для бота
PHOTO_START = os.getenv("PHOTO_START")
PHOTO_HELP = os.getenv("PHOTO_HELP")
PHOTO_INFO = os.getenv("PHOTO_INFO")
PHOTO_ERROR = os.getenv("PHOTO_ERROR")

SAPPORT_URL = os.getenv("SAPPORT_URL")

BASE_URL = os.getenv("BASE_URL")

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

IMAGEKIT_CACHEFILE_DIR = 'media/CACHE/images'
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = 'imagekit.cachefiles.strategies.Optimistic'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 минут по умолчанию
    }
}