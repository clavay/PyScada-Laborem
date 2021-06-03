#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Django settings for PyScadaServer project.

Generated by 'django-admin startproject' using Django 2.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import pyvisa
import importlib.util

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pyscada.core',
    'pyscada.modbus',
    'pyscada.phant',
    'pyscada.visa',
    'pyscada.hmi',
    'pyscada.systemstat',
    'pyscada.export',
    'pyscada.onewire',
    'pyscada.smbus',
]

if importlib.util.find_spec('pyscada.gpio') is not None:
    INSTALLED_APPS += [
        'pyscada.gpio',
    ]

if importlib.util.find_spec('pyscada.scripting') is not None:
    INSTALLED_APPS += [
        'pyscada.scripting',
    ]

if importlib.util.find_spec('pyscada.laborem') is not None:
    INSTALLED_APPS += [
        'pyscada.laborem',
    ]

if importlib.util.find_spec('django_cas_ng') is not None:
    INSTALLED_APPS += [
        'django_cas_ng',
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


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

if importlib.util.find_spec('django_cas_ng') is not None:
    AUTHENTICATION_BACKENDS += [
        'django_cas_ng.backends.CASBackend',
    ]
    CAS_SERVER_URL = 'https://sso.univ-pau.fr/cas/'
    CAS_VERSION = '2'
    CAS_EXTRA_LOGIN_KWARGS = {'proxies': {'https': 'http://cache.iutbayonne.univ-pau.fr:3128'}, 'timeout': 5}

    UNAUTHENTICATED_REDIRECT = '/accounts/choose_login/'


ROOT_URLCONF = 'PyScadaServer.urls'

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

WSGI_APPLICATION = 'PyScadaServer.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'PyScada_db',
        'USER':     'PyScada-user',
        'PASSWORD': 'PyScada-user-password',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }

        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = '/var/www/pyscada/http/static/'

MEDIA_URL = '/media/'

MEDIA_ROOT = '/var/www/pyscada/http/media/'

# PyScada settings
# https://github.com/trombastic/PyScada

# email settings
DEFAULT_FROM_EMAIL = ''
EMAIL_HOST = ''
EMAIL_PORT = 465
EMAIL_HOST_USER = 'r'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_PASSWORD = ''
EMAIL_PREFIX = 'PREFIX'  # Mail subject will be "PREFIX subjecttext"

# meta information's about the plant site
PYSCADA_META = {
    'name': 'A SHORT NAME',
    'description': 'A SHORT DESCRIPTION',
}

# export properties

PYSCADA_EXPORT = {
    'file_prefix': 'PREFIX_',
    'output_folder': '~/measurement_data_dumps',
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/pyscada_debug.log',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'pyscada': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'gunicorn': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

VISA_DEVICE_SETTINGS = {
    'USB0': {
        'open_timeout': 5000,
        'timeout': 15000,
    },
    'GPIB0': {
        'open_timeout': 5000,
        'timeout': 15000,
    },
    'ASRL/dev/ttyAMA0': {
        'baud_rate': 9600,
        'data_bits': 8,
        'parity': pyvisa.constants.Parity.none,
        'stop_bits': pyvisa.constants.StopBits.one,
        'write_termination': '',
    },
    'ASRL/dev/ttyUSB0': {
        'open_timeout': 5000,
    },
}
