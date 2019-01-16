from importlib import import_module
from typing import Iterable


def get_module_url_patterns(*modules: Iterable[str]) -> Iterable:
    patterns = []

    for module in modules:
        urlconf_module = import_module(module)
        patterns += getattr(urlconf_module, 'urlpatterns', None)

    return patterns
