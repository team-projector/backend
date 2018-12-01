import imp
import os
from importlib import import_module


def path_for_import(name):
    return os.path.dirname(os.path.abspath(import_module(name).__file__))


def find_module(name):
    modules = name.split('.')
    path = None
    file, pathname, description = None, None, None

    # FIX fix deprecated
    for name in modules:
        file, pathname, description = imp.find_module(name, path)
        path = [pathname]
    return file, pathname, description


def load_module_from_app(app, module):
    name = f'{app}.{module}'

    try:
        find_module(name)
    except ImportError:
        return None
    else:
        return import_module(name)
