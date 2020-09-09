# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime
from typing import Optional

from constance import LazyConfig
from constance.admin import Config, ConstanceAdmin
from django import forms
from django.contrib import admin
from django.utils.formats import localize
from django.utils.translation import ugettext_lazy as _

config = LazyConfig()

CALENDAR_CONFIG_NAMES = ("WEEKENDS_DAYS",)


class ConfigurationAdmin(ConstanceAdmin):
    """Configuration admin."""

    def get_config_value(self, name, options, form, initial):
        """Override from parent."""
        default, help_text = (
            self._update_default_value(name, options[0]),
            options[1],
        )
        source_value = initial.get(name)

        if source_value is None:
            source_value = getattr(config, name)

        return {
            "name": name,
            "default": localize(default),
            "raw_default": default,
            "help_text": _(help_text),
            "value": localize(source_value),
            "modified": localize(source_value) != localize(default),
            "form_field": form[name],
            "is_date": isinstance(default, date),
            "is_datetime": isinstance(default, datetime),
            "is_checkbox": isinstance(
                form[name].field.widget, forms.CheckboxInput,
            ),
            "is_file": isinstance(form[name].field.widget, forms.FileInput),
        }

    def _update_default_value(self, name, default) -> Optional[object]:
        """Update defaults for calendar."""
        if default and name in CALENDAR_CONFIG_NAMES:
            default = tuple(calendar.day_name[day] for day in default)

        return default


admin.site.unregister([Config])
admin.site.register([Config], ConfigurationAdmin)
