# -*- coding: utf-8 -*-

import calendar
from collections import OrderedDict

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

WEEK_DAYS = (
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
    "SUNDAY",
)

empty_default_str = ("", "", str)

CONSTANCE_ADDITIONAL_FIELDS = {
    "weekend_days": (
        "django.forms.MultipleChoiceField",
        {
            "required": True,
            "choices": [(getattr(calendar, day), day) for day in WEEK_DAYS],
        },
    ),
    "str_required": (
        "django.forms.CharField",
        {
            "widget": "django.forms.Textarea",
            "required": True,
            "widget_kwargs": {"attrs": {"rows": 3}},
        },
    ),
}

CONSTANCE_CONFIG = {
    "WEEKENDS_DAYS": (
        (calendar.SATURDAY, calendar.SUNDAY),
        "",
        "weekend_days",
    ),
    "GITLAB_ADDRESS": ("https://gitlab.com", "", str),
    "GITLAB_SYNC": (True, "", bool),
    "GITLAB_TOKEN": ("", "", "str_required"),
    "GITLAB_WEBHOOK_SECRET_TOKEN": empty_default_str,
    "GITLAB_ADD_WEBHOOKS": (False, "", bool),
    "OAUTH_GITLAB_KEY": empty_default_str,
    "OAUTH_GITLAB_SECRET": empty_default_str,
    "SLACK_TOKEN": empty_default_str,
    # email
    "EMAIL_HOST": empty_default_str,
    "EMAIL_PORT": empty_default_str,
    "EMAIL_HOST_USER": empty_default_str,
    "EMAIL_HOST_PASSWORD": empty_default_str,
    "EMAIL_USE_TLS": (True, "", bool),
    "DEFAULT_FROM_EMAIL": empty_default_str,
}

CONSTANCE_CONFIG_FIELDSETS = OrderedDict(
    (
        ("System", ("WEEKENDS_DAYS",)),
        (
            "Gitlab",
            (
                "GITLAB_ADDRESS",
                "GITLAB_SYNC",
                "GITLAB_TOKEN",
                "GITLAB_WEBHOOK_SECRET_TOKEN",
                "GITLAB_ADD_WEBHOOKS",
                "OAUTH_GITLAB_KEY",
                "OAUTH_GITLAB_SECRET",
            ),
        ),
        ("Notifications", ("SLACK_TOKEN",)),
        (
            "Email",
            (
                "EMAIL_HOST",
                "EMAIL_PORT",
                "EMAIL_HOST_USER",
                "EMAIL_HOST_PASSWORD",
                "EMAIL_USE_TLS",
                "DEFAULT_FROM_EMAIL",
            ),
        ),
    ),
)
