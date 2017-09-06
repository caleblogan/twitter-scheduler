"""
Django settings for twitter_site project.

Generated by 'django-admin startproject' using Django 1.11.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


def get_from_env(name, default=None):
    try:
        return os.environ[name]
    except KeyError as e:
        if DEBUG:
            return default
        else:
            raise KeyError(e)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_from_env('DJANGO_SECRET_KEY', 'nice')


ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'twitterscheduler.apps.TwitterschedulerConfig',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # all-auth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.twitter',
]

SITE_ID = 2

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'twitter_site.urls'

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

WSGI_APPLICATION = 'twitter_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_from_env('POSTGRES_NAME', 'postgres'),
        'USER': get_from_env('POSTGRES_USER', 'postgres'),
        'PASSWORD': get_from_env('POSTGRES_PASSWORD', 'nice_pass'),
        'HOST': get_from_env('POSTGRES_HOST', '192.168.99.100'),
        'PORT': get_from_env('POSTGRES_PORT', '5433'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

LOGIN_REDIRECT_URL = '/scheduler/'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# CELERY_BROKER_URL = 'amqp://guest:guest@rabbit:5672/'
# CELERY_BROKER_URL = 'amqp://guest:guest@192.168.99.100:5672/'
CELERY_BROKER_URL = 'amqp://{user}:{password}@{hostname}:{port}/'.format(
    user=get_from_env('RABBITMQ_DEFAULT_USER', 'guest'),
    password=get_from_env('RABBITMQ_DEFAULT_PASS', 'guest'),
    hostname=get_from_env('RABBITMQ_HOSTNAME', '192.168.99.100'),
    port=get_from_env('RABBITMQ_PORT', '5672'),
)
CELERY_TIMEZONE = TIME_ZONE
