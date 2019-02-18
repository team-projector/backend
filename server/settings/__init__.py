from os import environ

from decouple import AutoConfig
from split_settings.tools import include

from server import BASE_DIR

config = AutoConfig(search_path=BASE_DIR.joinpath('config'))

ENV = environ.get('DJANGO_ENV') or 'dev'

base_settings = [
    'components/*.py',
    f'environments/{ENV}.py',
]

include(*base_settings, scope=globals())
