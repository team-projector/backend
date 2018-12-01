from os import environ

from split_settings.tools import include

ENV = environ.get('DJANGO_ENV') or 'local'

base_settings = [
    'components/*.py',
    f'environments/{ENV}.py',
]

include(*base_settings, scope=globals())
