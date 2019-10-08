# -*- coding: utf-8 -*-

from contextlib import suppress
from importlib import import_module
from typing import Iterable, List


def get_module_url_patterns(*modules: str) -> Iterable:
    """Get url_patterns of modules."""
    patterns: List = []

    for module in modules:
        urlconf_module = import_module(module)
        patterns += getattr(urlconf_module, 'urlpatterns', None)

    return patterns


def load_module_from_app(
    app: str,
    module: str,
):
    """Load module from application."""
    with suppress(ModuleNotFoundError):
        return import_module(f'{app}.{module}')
