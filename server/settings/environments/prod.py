import os

DEBUG = True

SITE_ID = 1

USE_TZ = True
TIME_ZONE = 'Europe/Moscow'

LANGUAGE_CODE = 'en'

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DJANGO_DATABASE_NAME'),
        'USER': os.getenv('DJANGO_DATABASE_USER'),
        'PASSWORD': os.getenv('DJANGO_DATABASE_PASSWORD'),
        'HOST': os.getenv('DJANGO_DATABASE_HOST'),
        'PORT': os.getenv('DJANGO_DATABASE_PORT', '5432')
    }
}
