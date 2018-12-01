DEBUG = False

SECRET_KEY = 'test.secret.key'

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'en'

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postrges',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
    }
}

CELERY_TASK_ALWAYS_EAGER = True

BASE_URL = 'http://localhost:8000'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    },
}
