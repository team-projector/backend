SITE_ID = 1

DEBUG = True

LANGUAGE_CODE = 'en'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost'
    }
}

SECRET_KEY = 'secret.key'
