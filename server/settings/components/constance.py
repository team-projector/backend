import calendar
from collections import OrderedDict

from django.db import models

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"


class Currency(models.TextChoices):
    """Currency choices."""

    RUR = "rur", "₽"  # noqa: WPS115
    USD = "usd", "$"  # noqa: WPS115
    EUR = "eur", "€"  # noqa: WPS115


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
    "first_week_day": (
        "django.forms.ChoiceField",
        {
            "required": True,
            "choices": [(0, WEEK_DAYS[6]), (1, WEEK_DAYS[0])],
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
    "gitlab_root_groups": (
        "apps.core.models.fields.integer_array.IntegerArrayField",
        {"min_value": 1, "required": False},
    ),
    "gitlab_sync_start_date": (
        "django.forms.DateField",
        {
            "widget": "django.contrib.admin.widgets.AdminDateWidget",
            "required": False,
        },
    ),
    "currency_code": (
        "django.forms.ChoiceField",
        {
            "required": True,
            "choices": Currency.choices,
        },
    ),
}

CONSTANCE_CONFIG = {
    "WEEKENDS_DAYS": (
        (calendar.SATURDAY, calendar.SUNDAY),
        "",
        "weekend_days",
    ),
    "FIRST_WEEK_DAY": (calendar.MONDAY, "", "first_week_day"),
    "CURRENCY_CODE": (Currency.USD.value, "", "currency_code"),
    "DEMO_MODE": (False, "", bool),
    "GITLAB_ADDRESS": ("https://gitlab.com", "", str),
    "GITLAB_SYNC": (True, "", bool),
    "GITLAB_TOKEN": ("", "", "str_required"),
    "GITLAB_WEBHOOK_SECRET_TOKEN": empty_default_str,
    "GITLAB_ADD_WEBHOOKS": (False, "", bool),
    "GITLAB_ROOT_GROUPS": (
        "",
        "Comma separated array of gitlab group's ids",
        "gitlab_root_groups",
    ),
    "GITLAB_SYNC_START_DATE": ("", "", "gitlab_sync_start_date"),
    "OAUTH_GITLAB_KEY": empty_default_str,
    "OAUTH_GITLAB_SECRET": empty_default_str,
    "GITLAB_LOGIN_ENABLED": (True, "", bool),
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
        (
            "System",
            ("WEEKENDS_DAYS", "FIRST_WEEK_DAY", "CURRENCY_CODE", "DEMO_MODE"),
        ),
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
                "GITLAB_ROOT_GROUPS",
                "GITLAB_SYNC_START_DATE",
                "GITLAB_LOGIN_ENABLED",
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
