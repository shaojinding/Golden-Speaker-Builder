"""
Django settings for speech_project project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6@k$*+$28u-g&k2u7q5j+iel2n!ui9du51$4kqpk805i0^e2*q'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'speech',
    'mpd',
    'django_auth0',
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

# STATICFILES_FINDERS = [
#     'django.contrib.staticfiles.finders.FileSystemFinder',
#     'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#     'npm.finders.NpmFinder',
# ]

ROOT_URLCONF = 'speech_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_auth0.context_processors.auth0',
            ],
        },
    },
]

WSGI_APPLICATION = 'speech_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
    # {
    #     'NAME': 'django_auth0.auth_backend.Auth0Backend',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/


STATIC_PATH = os.path.join(BASE_DIR,'static')

STATIC_URL = '/static/' # You may find this is already defined as such.

STATICFILES_DIRS = (
    STATIC_PATH,
)

TIME_ZONE = 'America/Chicago'

# STATIC_ROOT = '/home/shjd/golden-speaker/static_root/'
STATIC_ROOT = '/var/golden-speaker-static/'

# STATICFILES_DIRS = '/home/shjd/golden-speaker/static_root/'

AUTH0_INDEX_URL = 'https://goldenspeaker.las.iastate.edu'
AUTH0_CALLBACK_URL = 'https://goldenspeaker.las.iastate.edu/auth/callback/?'

# AUTH0_INDEX_URL = 'http://127.0.0.1:8000'
#
# AUTH0_CALLBACK_URL = 'http://127.0.0.1:8000/auth/callback/?'

AUTH0_CLIENT_ID = 'GfnvKP8rFiGCaBXauuNEulqY8EapxJmp'

AUTH0_SECRET = 'Gdchw6JMGrOyRkMwre1IIYm2XYshOn9iXaN_av-2hNjGoZLUP0eUvibV9BW871_W'

AUTH0_DOMAIN = 'shjd.auth0.com'

AUTH0_SUCCESS_URL = '/speech/'

LOGIN_URL = '/auth/login/'

DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800


# DJANGO-NPM
# NPM_ROOT_PATH = os.path.join(BASE_DIR,'static')
