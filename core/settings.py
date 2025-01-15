"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""


from decouple import config
from pathlib import Path
from datetime import timedelta 
import os
from dotenv import load_dotenv
from core.utils.ckeditor import *




# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-58pn7pvl9xa3i5)0%@)89or60py7a0^0h+!*)x6h=pilpr40!5'

#STRIPE_SECRET_KEY
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
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
    'cloudinary_storage',
    'cloudinary',
    'rest_framework',
    'rest_framework_simplejwt',
    "drf_spectacular",
    "corsheaders",
    'django_celery_beat',
    'taggit',
    'django_ckeditor_5',
    'ckeditor_uploader',
    
    

    # Custom apps
    'users',
    'saloons',
    'country',
    'appointments',
    'services',
    'staffs',
    'review',
    'search',
    'newsletter',
    'offers',
    'openinghours',
    'payments',
    'moreclub',
    'meta',
    'userdashboard'
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.utils.country_middleware.CountryDomainMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'core.urls'

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
            ],
        },
    },
]

AUTH_USER_MODEL = "users.User"

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default backend
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', 
        'NAME': 'moresaloon4',              
        'USER': 'moresaloon4',                
        'PASSWORD': 'NY48FX7f6Xde',     
        'HOST': '100.42.187.204',            
        'PORT': '5432',                            
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql', 
#         'NAME': 'salonnewdb',              
#         'USER': 'salonnewdb',                
#         'PASSWORD': '2kZTjtrFbirR',     
#         'HOST': '100.42.187.204',            
#         'PORT': '5432',                            
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dvmqwrhbx',
    'API_KEY': '831421472727561',
    'API_SECRET': 'IeJhUr7jhK9-qU-yjm3n_xGG3Js',
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

if DEBUG:
    # STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3001",
    "http://localhost:3000",
    "http://192.168.1.101:3000",
     "http://192.168.1.101:3001",
    "http://192.168.1.74:8000",
    "https://more-saloon.vercel.app",
    "https://www.moredealsclub.com",
    "https://moresalons.com",
    "https://admin-panel-tau-drab.vercel.app",
    "https://web-production-f5d1.up.railway.app"



]

CORS_ALLOW_CREDENTIALS = True


CORS_ALLOWED_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

CORS_ALLOW_HEADERS = [
    'authorization',
    'content-type',
    'X-Country-Code',
]


# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.utils.sso_middleware.SSOAuthentication',
    ],
    "DEFAULT_SCHEMA_CLASS":
    "drf_spectacular.openapi.AutoSchema",
    "DATETIME_FORMAT":
    "%Y-%m-%dT%H:%M:%S",
    "TEST_REQUEST_DEFAULT_FORMAT":
    "json",
    "DEFAULT_PAGINATION_CLASS":
    "rest_framework.pagination.LimitOffsetPagination",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "MoreTechGlobal User Modules API Document",
    "DESCRIPTION": "Welcome to MoreTechGlobal Centeral Authentication Service",
    "VERSION": "1.0.0",
    "SWAGGER_UI_FAVICON_HREF": None,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SSO_SERVICE_URL = 'https://moretrek.com/api/'

CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000/', 'https://salon.moretechglobal.com']
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

