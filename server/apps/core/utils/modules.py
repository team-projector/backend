# -*- coding: utf-8 -*-

import importlib


def load_module_from_app(app: str, dotted_path: str):
    """Load module from application."""
    module_name = "{0}.{1}".format(app, dotted_path)
    module_spec = importlib.util.find_spec(module_name)  # type: ignore

    if module_spec:
        return importlib.import_module(module_name)
