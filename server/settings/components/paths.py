import os
from os.path import abspath, dirname, join

from server import BASE_DIR

STATIC_ROOT = BASE_DIR.joinpath('run', 'static')
MEDIA_ROOT = BASE_DIR.joinpath('run', 'media')

DJANGO_ROOT = dirname(dirname(dirname(abspath(__file__))))
PROJECT_ROOT = dirname(DJANGO_ROOT)

PROJECT_TEMPLATES = [
    join(PROJECT_ROOT, 'templates'),
]

LOGGING_PATH = BASE_DIR.joinpath('logs')

if not os.path.exists(LOGGING_PATH):
    os.makedirs(LOGGING_PATH)
