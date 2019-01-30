import os

from server import BASE_DIR

LOGGING_PATH = BASE_DIR.joinpath('logs')

if not os.path.exists(LOGGING_PATH):
    os.makedirs(LOGGING_PATH)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s]|%(levelname)s|%(module)s.%(funcName)s:%(lineno)s|%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
