"""
Django settings for the Mini-PSF (Protein Scaffold Filling) project.

Works for BOTH local development and production deployment.
Production-specific values are read from environment variables.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# Security
# -------------------------------------------------------------------
# In production, set DJANGO_SECRET_KEY as an environment variable.
# Locally, the fallback key below is fine.
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'demo-key-do-not-use-in-production-protein-scaffold-filling'
)

# DEBUG is True locally but False in production.
# Set DJANGO_DEBUG=False on your deployment host.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# Allowed hosts: '*' locally, your real domain in production.
# Set DJANGO_ALLOWED_HOSTS='yourapp.onrender.com,yourdomain.com' in production.
ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    '*'
).split(',')

# CSRF trusted origins — required when serving over HTTPS in production.
# Set DJANGO_CSRF_TRUSTED_ORIGINS='https://yourapp.onrender.com' in production.
_csrf_env = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://localhost:8000',
    'https://127.0.0.1:8000',
]
if _csrf_env:
    CSRF_TRUSTED_ORIGINS.extend(_csrf_env.split(','))

# GitHub Codespaces uses dynamic *.app.github.dev URLs — trust them automatically.
CODESPACE_NAME = os.environ.get('CODESPACE_NAME')
if CODESPACE_NAME:
    codespace_origin = f'https://{CODESPACE_NAME}-8000.app.github.dev'
    CSRF_TRUSTED_ORIGINS.append(codespace_origin)
    ALLOWED_HOSTS.append(f'{CODESPACE_NAME}-8000.app.github.dev')

# -------------------------------------------------------------------
# Apps & middleware
# -------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'scaffold_filler',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise serves static files (CSS, JS) in production.
    # It MUST come right after SecurityMiddleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'scaffold_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'scaffold_app.wsgi.application'

# -------------------------------------------------------------------
# Database — SQLite is fine for this demo.
# Note: on Render/Railway the SQLite file resets on each deploy.
# For a class demo that's fine; for real production use PostgreSQL.
# -------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static files (CSS) — WhiteNoise compresses and caches these.
# -------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'   # `collectstatic` writes here
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
