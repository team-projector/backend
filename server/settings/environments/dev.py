from server import BASE_DIR

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'team_projector',
        'USER': 'postgres',
        'PASSWORD': 'pass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CELERY_TASK_ALWAYS_EAGER = True

STATIC_ROOT = BASE_DIR.joinpath('static')

SECRET_KEY = 'dev'

GITLAB_TOKEN = ''
