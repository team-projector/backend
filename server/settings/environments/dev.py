SITE_ID = 1
SITE_DOMAIN = 'tp.junte.it'

DEBUG = True

USE_TZ = False

LANGUAGE_CODE = 'en'

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'projector',
        'USER': 'admin',
        'PASSWORD': '229835',
        'HOST': 'localhost'
    }
}

SECRET_KEY = 'secret.key'

CELERY_TASK_ALWAYS_EAGER = True

GITLAB_TOKEN = 'M6wM1-ZeeCPzPm4Z9PzS'
GITLAB_CHECK_WEBHOOKS = True
