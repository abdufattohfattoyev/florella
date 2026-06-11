import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-hcj*fch^)c^*8t_tf8s7w0aul8a_gi4!vx7itvcojy!zisct8r')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

CSRF_TRUSTED_ORIGINS = [
    'https://florella-cafe.uz',
    'https://www.florella-cafe.uz',
]

# Nginx reverse proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ─── Sessiya — mijoz akkauntdan tez chiqib ketmasligi uchun ─────────────────
SESSION_COOKIE_AGE = 60 * 60 * 24 * 90      # 90 kun
SESSION_EXPIRE_AT_BROWSER_CLOSE = False     # brauzer yopilsa ham saqlanadi
SESSION_SAVE_EVERY_REQUEST = True           # har faollikda muddat qayta 90 kunga uzayadi
SESSION_COOKIE_SAMESITE = 'Lax'


INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'menu',
    'orders',
    'tgauth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'menu.context_processors.upsell_items',
                'tgauth.context_processors.customer_profile',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Telegram xabarnoma ─────────────────────────────────────────────────────
# @BotFather dan token, @userinfobot dan o'z ID'ingizni oling.
# Bir nechta admin bo'lsa ID'larni vergul bilan ajrating: 111,222
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_ADMIN_IDS = os.environ.get('TELEGRAM_ADMIN_IDS', '')

# ─── Yandex Geocoder (manzil aniqlash — uy raqamigacha) ─────────────────────
# Bepul kalit: developer.tech.yandex.ru -> JavaScript API va Geocoder HTTP API
YANDEX_GEOCODER_KEY = os.environ.get('YANDEX_GEOCODER_KEY', '')

# ─── Jazzmin ───────────────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title": "Флорелла Кафе",
    "site_header": "Флорелла Кафе",
    "site_brand": "🌸 Флорелла",
    "site_logo": None,
    "login_logo": None,
    "welcome_sign": "Хуш келибсиз, бошқарув панелига!",
    "copyright": "Флорелла Кафе © 2026",
    "search_model": ["menu.MenuItem", "orders.Order"],
    "user_avatar": None,

    "topmenu_links": [
        {"name": "Сайт",  "url": "/",        "new_window": True},
        {"name": "Меню",  "url": "/menu/",   "new_window": False, "model": "menu.MenuItem"},
        {"model": "auth.User"},
    ],

    "usermenu_links": [
        {"name": "Сайтга ўтиш", "url": "/", "new_window": True, "icon": "fas fa-external-link-alt"},
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],

    "order_with_respect_to": [
        "menu", "menu.Category", "menu.MenuItem",
        "orders", "orders.Order", "orders.OrderItem",
    ],

    "icons": {
        "auth":              "fas fa-users-cog",
        "auth.user":         "fas fa-user",
        "auth.Group":        "fas fa-users",
        "menu":              "fas fa-book-open",
        "menu.Category":     "fas fa-th-large",
        "menu.MenuItem":     "fas fa-utensils",
        "orders":            "fas fa-receipt",
        "orders.Order":      "fas fa-shopping-cart",
        "orders.OrderItem":  "fas fa-list-ul",
        "orders.TelegramSettings": "fab fa-telegram",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    "related_modal_active": True,
    "custom_css": "css/admin_orders.css",
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-warning",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-warning",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary":   "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info":      "btn-outline-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
    "actions_sticky_top": True,
}
