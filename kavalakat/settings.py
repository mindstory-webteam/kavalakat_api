# # -----------------------------------digital ocean--------------------------------

# import os
# from pathlib import Path
# from datetime import timedelta
# import dj_database_url
# from dotenv import load_dotenv

# # ── Load .env file from project root ─────────────────────────────────────────
# BASE_DIR = Path(__file__).resolve().parent.parent
# load_dotenv(os.path.join(BASE_DIR, '.env'))

# # ── Core ──────────────────────────────────────────────────────────────────────
# SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me')
# DEBUG      = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS = os.environ.get(
#     'ALLOWED_HOSTS',
#     'localhost,127.0.0.1,api.kavalakat.com'
# ).split(',')

# # ── CSRF Trusted Origins ──────────────────────────────────────────────────────
# # Required for Django 4.0+ — fixes 403 CSRF error on api.kavalakat.com
# CSRF_TRUSTED_ORIGINS = os.environ.get(
#     'CSRF_TRUSTED_ORIGINS',
#     'https://api.kavalakat.com,https://tan-rail-168119.hostingersite.com'
# ).split(',')

# # ── Installed Apps ────────────────────────────────────────────────────────────
# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',

#     # Third-party
#     'rest_framework',
#     'rest_framework_simplejwt',
#     'rest_framework_simplejwt.token_blacklist',
#     'corsheaders',
#     'django_filters',

#     # Local apps
#     'pages.apps.PagesConfig',
#     'about.apps.AboutConfig',
#     'portfolio.apps.PortfolioConfig',
#     'blog.apps.BlogConfig',
#     'contact.apps.ContactConfig',
#     'ai_module.apps.AiModuleConfig',
#     'dashboard.apps.DashboardConfig',
# ]

# # ── Middleware ────────────────────────────────────────────────────────────────
# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'whitenoise.middleware.WhiteNoiseMiddleware',
#     'corsheaders.middleware.CorsMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF     = 'kavalakat.urls'
# WSGI_APPLICATION = 'kavalakat.wsgi.application'

# # ── Templates ─────────────────────────────────────────────────────────────────
# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [BASE_DIR / 'templates'],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#                 'dashboard.context_processors.dashboard_globals',
#             ],
#         },
#     },
# ]

# # ── Database ──────────────────────────────────────────────────────────────────
# # LOCAL:         postgresql://kavalakat_user1:kavalakat@localhost:5432/kavalakat_new
# # DIGITALOCEAN:  postgresql://kavalakat_user:password@localhost:5432/kavalakat_db
# DATABASE_URL = os.environ.get(
#     'DATABASE_URL',
#     'postgresql://kavalakat_user1:kavalakat@localhost:5432/kavalakat_new'
# )
# DATABASES = {
#     'default': dj_database_url.parse(
#         DATABASE_URL,
#         conn_max_age=60,   # keep connections alive 60 sec (safe for Droplet)
#         ssl_require=False, # no SSL needed for local PostgreSQL on same server
#     )
# }

# # ── Auth / Password Validation ────────────────────────────────────────────────
# AUTH_PASSWORD_VALIDATORS = [
#     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
# ]

# # ── Django REST Framework ─────────────────────────────────────────────────────
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ),
#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticatedOrReadOnly',
#     ),
#     'DEFAULT_PAGINATION_CLASS': 'kavalakat.pagination.StandardPagination',
#     'DEFAULT_FILTER_BACKENDS': [
#         'django_filters.rest_framework.DjangoFilterBackend',
#         'rest_framework.filters.SearchFilter',
#         'rest_framework.filters.OrderingFilter',
#     ],
#     'DEFAULT_RENDERER_CLASSES': [
#         'rest_framework.renderers.JSONRenderer',
#     ],
#     'DEFAULT_PARSER_CLASSES': [
#         'rest_framework.parsers.JSONParser',
#         'rest_framework.parsers.MultiPartParser',
#         'rest_framework.parsers.FormParser',
#     ],
#     'EXCEPTION_HANDLER': 'kavalakat.exceptions.custom_exception_handler',
# }

# # ── Simple JWT ────────────────────────────────────────────────────────────────
# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME':    timedelta(hours=2),
#     'REFRESH_TOKEN_LIFETIME':   timedelta(days=7),
#     'ROTATE_REFRESH_TOKENS':    True,
#     'BLACKLIST_AFTER_ROTATION': True,
#     'UPDATE_LAST_LOGIN':        True,
#     'AUTH_HEADER_TYPES':        ('Bearer',),
# }

# # ── CORS ──────────────────────────────────────────────────────────────────────
# CORS_ALLOWED_ORIGINS = os.environ.get(
#     'CORS_ALLOWED_ORIGINS',
#     'http://localhost:3000,http://127.0.0.1:3000,https://tan-rail-168119.hostingersite.com'
# ).split(',')
# CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOW_METHODS     = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
# CORS_ALLOW_HEADERS     = ['accept', 'authorization', 'content-type', 'origin', 'x-requested-with']

# # ── Static / Media ────────────────────────────────────────────────────────────
# STATIC_URL          = '/static/'
# STATIC_ROOT         = BASE_DIR / 'staticfiles'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# MEDIA_URL           = '/media/'
# MEDIA_ROOT          = BASE_DIR / 'media'

# # ── Internationalisation ──────────────────────────────────────────────────────
# LANGUAGE_CODE      = 'en-us'
# TIME_ZONE          = 'Asia/Kolkata'
# USE_I18N           = True
# USE_TZ             = True
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# MESSAGE_STORAGE    = 'django.contrib.messages.storage.session.SessionStorage'

# # ── OpenAI ────────────────────────────────────────────────────────────────────
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# # ── Security Settings ─────────────────────────────────────────────────────────
# # Running on DigitalOcean Droplet with Nginx (HTTP only for now)
# # Enable HTTPS settings only after adding SSL certificate with Certbot
# if not DEBUG:
#     # Basic security headers — safe for HTTP Droplet
#     SECURE_CONTENT_TYPE_NOSNIFF = True
#     X_FRAME_OPTIONS             = 'DENY'

#     # ── Disable HTTPS enforcement (no SSL certificate yet) ────────────────────
#     SECURE_SSL_REDIRECT            = False
#     SECURE_HSTS_SECONDS            = 0    # set to 31536000 AFTER adding SSL
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = False
#     SECURE_PROXY_SSL_HEADER        = None

#     # ── Cookies — use False until HTTPS is set up ─────────────────────────────
#     SESSION_COOKIE_SECURE  = False  # set True after SSL
#     SESSION_COOKIE_SAMESITE = 'Lax'
#     CSRF_COOKIE_SECURE     = False  # set True after SSL
#     CSRF_COOKIE_SAMESITE   = 'Lax'

# # ── Logging ───────────────────────────────────────────────────────────────────
# LOGGING = {
#     'version':                  1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '[{levelname}] {asctime} {module}: {message}',
#             'style':  '{',
#         },
#     },
#     'handlers': {
#         'console': {
#             'class':     'logging.StreamHandler',
#             'formatter': 'verbose',
#         },
#         'file': {
#             'class':     'logging.FileHandler',
#             'filename':  '/var/log/kavalakat_django.log',
#             'formatter': 'verbose',
#         },
#     },
#     'root': {
#         'handlers': ['console', 'file'],
#         'level':    'INFO',
#     },
#     'loggers': {
#         'django': {
#             'handlers':  ['console', 'file'],
#             'level':     'WARNING',
#             'propagate': False,
#         },
#         'ai_module': {
#             'handlers':  ['console', 'file'],
#             'level':     'DEBUG',
#             'propagate': False,
#         },
#     },
# }

# # --------------------------------renderrrrr----------------------------------------
import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR   = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me')
DEBUG      = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,.onrender.com'
).split(',')


# ── Installed Apps ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Local apps
    'pages.apps.PagesConfig',
    'about.apps.AboutConfig',
    'portfolio.apps.PortfolioConfig',
    'blog.apps.BlogConfig',
    'contact.apps.ContactConfig',
    'ai_module.apps.AiModuleConfig',
    'dashboard.apps.DashboardConfig',
    'services.apps.ServicesConfig',
]


# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # ← MUST be FIRST
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF     = 'kavalakat.urls'
WSGI_APPLICATION = 'kavalakat.wsgi.application'


# ── Templates ─────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashboard.context_processors.dashboard_globals',
            ],
        },
    },
]


# ── Database ──────────────────────────────────────────────────────────────────
# LOCAL:  postgresql://kavalakat_user1:kavalakat@localhost:5432/kavalakat_new
# RENDER: set DATABASE_URL in Render environment variables
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://kavalakat_user1:kavalakat@localhost:5432/kavalakat_new'
)
DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=0,    # fresh connection each request (required for Render free tier)
        ssl_require=False, # Render handles SSL at proxy level
    )
}


# ── Auth / Password Validation ────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ── Django REST Framework ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'kavalakat.pagination.StandardPagination',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'kavalakat.exceptions.custom_exception_handler',
}


# ── drf-spectacular (API Documentation) ──────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE':       'Kavalakat API',
    'DESCRIPTION': (
        'REST API for Kavalakat CMS — covers Pages, About, Portfolio, '
        'Blog, Contact, Careers, Enquiries and AI Module.'
    ),
    'VERSION':               '1.0.0',
    'SERVE_INCLUDE_SCHEMA':  False,
    'CONTACT': {
        'name':  'Kavalakat Dev Team',
        'email': 'dev@kavalakat.com',
    },
    'LICENSE': {
        'name': 'Proprietary',
    },
    'TAGS': [
        {'name': 'auth',      'description': 'JWT authentication endpoints'},
        {'name': 'pages',     'description': 'Static page management'},
        {'name': 'about',     'description': 'About, Strengths, Milestones, Projects, Team, Gallery'},
        {'name': 'portfolio', 'description': 'Portfolio categories and items'},
        {'name': 'blog',      'description': 'Blog posts and categories'},
        {'name': 'contact',   'description': 'Contact info, Office locations, Careers, Enquiries'},
        {'name': 'ai',        'description': 'AI module endpoints'},
    ],
    'COMPONENT_SPLIT_REQUEST':          True,
    'SORT_OPERATIONS':                  False,
    'ENUM_GENERATE_CHOICE_DESCRIPTION': True,
}


# ── Simple JWT ────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':    timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME':   timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':    True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN':        True,
    'AUTH_HEADER_TYPES':        ('Bearer',),
}


# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "https://tan-rail-168119.hostingersite.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "origin",
    "x-requested-with",
]


# ── Static / Media ────────────────────────────────────────────────────────────
STATIC_URL          = '/static/'
STATIC_ROOT         = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL           = '/media/'
MEDIA_ROOT          = BASE_DIR / 'media'


# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE      = 'en-us'
TIME_ZONE          = 'Asia/Kolkata'
USE_I18N           = True
USE_TZ             = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MESSAGE_STORAGE    = 'django.contrib.messages.storage.session.SessionStorage'


# ── OpenAI ────────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')


# ── Production Security (Render) ──────────────────────────────────────────────
if not DEBUG:
    SECURE_HSTS_SECONDS            = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT            = False      # Render handles HTTPS — do NOT redirect
    SECURE_PROXY_SSL_HEADER        = ('HTTP_X_FORWARDED_PROTO', 'https')  # trust Render proxy
    SESSION_COOKIE_SECURE          = True
    SESSION_COOKIE_SAMESITE        = 'Lax'
    CSRF_COOKIE_SECURE             = True
    CSRF_COOKIE_SAMESITE           = 'Lax'
    SECURE_CONTENT_TYPE_NOSNIFF    = True
    X_FRAME_OPTIONS                = 'DENY'


# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    'version':                  1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module}: {message}',
            'style':  '{',
        },
    },
    'handlers': {
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level':    'INFO',
    },
    'loggers': {
        'django': {
            'handlers':  ['console'],
            'level':     'WARNING',
            'propagate': False,
        },
        'ai_module': {
            'handlers':  ['console'],
            'level':     'DEBUG',
            'propagate': False,
        },
    },
}