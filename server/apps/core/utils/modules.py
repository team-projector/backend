# -*- coding: utf-8 -*-

from contextlib import suppress
from importlib import import_module


def load_module_from_app(
    app: str,
    module: str,
):
    """Load module from application."""
    with suppress(ModuleNotFoundError):
        return import_module(f'{app}.{module}')
