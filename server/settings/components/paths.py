from os.path import abspath, dirname

from server import BASE_DIR

DJANGO_ROOT = dirname(dirname(dirname(abspath(__file__))))
PROJECT_ROOT = dirname(DJANGO_ROOT)

STATIC_ROOT = BASE_DIR.joinpath('run', 'static')
MEDIA_ROOT = BASE_DIR.joinpath('run', 'media')
