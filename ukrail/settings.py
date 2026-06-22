"""
Django settings for UK Rail Live — production-ready, Vercel-compatible.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ──────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-insecure-key-change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,*.vercel.app').split(',')

# ── Apps ─────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.gis',
    'rest_framework',
    'corsheaders',
    'django_htmx',
    'rail',
]

# ── Middleware ───────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'ukrail.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'rail' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'rail.context_processors.ad_slots',
                'rail.context_processors.station_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'ukrail.wsgi.application'
ASGI_APPLICATION = 'ukrail.asgi.application'

# ── Database ─────────────────────────────────────────────────────────────
# Use PostGIS when DATABASE_URL is set (Neon / production), sqlite for local dev.
if os.environ.get('DATABASE_URL'):
    # Parse Neon/Postgres URL — django-fernet / dj-database-url style
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ['DATABASE_URL'],
            conn_max_age=600,
            conn_health_check=True,
        )
    }
    # PostGIS extension if using Postgres with it
    DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.spatialite',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Password validation ──────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ──────────────────────────────────────────────────
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_TZ = True

# ── Static files ─────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / 'rail' / 'static']

# ── Default primary key ──────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── REST Framework ───────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION': {
        'CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 50,
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# ── CORS ─────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ── Caching ──────────────────────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'uk-rail-live',
    }
}
CACHE_TIMEOUT = 60  # seconds — Darwin data refreshes every 30-60s

# ── Darwin API ────────────────────────────────────────────────────────────
DARWIN_API_KEY = os.environ.get('DARWIN_API_KEY', '')
DARWIN_API_URL = os.environ.get('DARWIN_API_URL', 'https://api1.raildata.org.uk/1010-knowledge1_1-rti')

# ── Security (production) ────────────────────────────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'

# ── Logging ──────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}