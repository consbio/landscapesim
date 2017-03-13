import os
import json

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.abspath(__file__)
for __ in range(3):
    BASE_DIR = os.path.dirname(BASE_DIR)

CONFIG = {}
config_file = os.path.join(BASE_DIR, 'config.json')
if config_file and os.path.isfile(config_file):
    with open(config_file) as f:
        CONFIG = json.loads(f.read())

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG.get('django_secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    'ncdjango',

    'rest_framework',
    'tastypie',

    'djcelery',                 # Celery backend, on linux we should use django_celery_results
    #'django_celery_results',

    'landscapesim'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'landscapesim_project.urls'

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

WSGI_APPLICATION = 'landscapesim_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': CONFIG.get('db_name', 'landscapesim'),
        'USER': CONFIG.get('db_user', 'landscapesim'),
        'PASSWORD': CONFIG.get('db_password'),
        'HOST': CONFIG.get('db_host', '127.0.0.1')
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

NC_INSTALLED_INTERFACES = (
    'ncdjango.interfaces.data',
    'ncdjango.interfaces.arcgis_extended',
    'ncdjango.interfaces.arcgis',
    'landscapesim.tiles'
)
