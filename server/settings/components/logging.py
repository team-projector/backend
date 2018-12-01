import os

from server.settings.components.paths import LOGGING_PATH

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
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_PATH, 'log.txt'),
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
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },

    },
}
