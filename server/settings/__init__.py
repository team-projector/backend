# -*- coding: utf-8 -*-

from os import environ

from split_settings.tools import include

ENV = environ.get('DJANGO_ENV') or 'development'

include(
    'components/*.py',
    f'environments/{ENV}.py',
)
