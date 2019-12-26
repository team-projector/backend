# -*- coding: utf-8 -*-

SECRET_KEY = 'test.key'  # noqa: S105

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postrges',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
    },
}

CELERY_TASK_ALWAYS_EAGER = True

BASE_URL = 'http://localhost:8000'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
