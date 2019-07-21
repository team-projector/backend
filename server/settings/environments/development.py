from server import BASE_DIR

DEBUG = True
ALLOWED_HOSTS = ['*']

DOMAIN_NAME = 'teamprojector.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'team-projector',
        'USER': 'admin',
        'PASSWORD': '229835',
        'HOST': 'localhost'
    },
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'team-projector',
    #     'USER': 'team-projector',
    #     'PASSWORD': 'aNRQHPu9yQSSNdzQ',
    #     'HOST': '68.183.223.198'
    # }
}

CELERY_TASK_ALWAYS_EAGER = True
STATIC_ROOT = BASE_DIR.joinpath('static')

SECRET_KEY = 'dev'

# GITLAB_CHECK_WEBHOOKS = True
GITLAB_TOKEN = 'M6wM1-ZeeCPzPm4Z9PzS'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s]|%(levelname)s|%(module)s.'
                      '%(funcName)s:%(lineno)s|%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'apps': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
    }
}
