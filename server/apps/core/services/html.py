# -*- coding: utf-8 -*-

import html


def unescape_text(source, field) -> None:
    """Unescaping text values in dict."""
    if isinstance(source, list):
        _unescape_text_list(source, field)
    elif isinstance(source, dict):
        _unescape_text_dict(source, field)


def _unescape_text_list(source, field) -> None:
    for source_object in source:
        unescape_text(source_object, field)


def _unescape_text_dict(source, field) -> None:
    for key, key_value in source.items():
        if key == field and isinstance(key_value, str):
            source[key] = html.unescape(key_value)
        elif isinstance(key_value, (list, dict)):
            unescape_text(key_value, field)
