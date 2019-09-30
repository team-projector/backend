# -*- coding: utf-8 -*-

from importlib import import_module
from importlib.util import find_spec
from typing import Iterable, List


def get_module_url_patterns(*modules: str) -> Iterable:
    patterns: List = []

    for module in modules:
        urlconf_module = import_module(module)
        patterns += getattr(urlconf_module, 'urlpatterns', None)

    return patterns


def load_module_from_app(
    app: str,
    module: str,
):
    name = f'{app}.{module}'

    try:
        find_spec(name)
    except ModuleNotFoundError:
        pass
    else:
        return import_module(name)
