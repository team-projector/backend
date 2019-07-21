from .production import STATIC_ROOT as PROD_STATIC_ROOT

SECRET_KEY = 'build'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy'
    }
}

STATIC_ROOT = PROD_STATIC_ROOT
