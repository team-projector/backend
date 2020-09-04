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
    "SYSTEM_USER": ("system", "", str),
    "GITLAB_ADDRESS": ("https://gitlab.com", "", str),
    "GITLAB_SYNC": (True, "", bool),
    "GITLAB_TOKEN": ("", "", "str_required"),
    "GITLAB_WEBHOOK_SECRET_TOKEN": ("", "", str),
    "GITLAB_ADD_WEBHOOKS": (False, "", bool),
    "OAUTH_GITLAB_KEY": ("", "", str),
    "OAUTH_GITLAB_SECRET": ("", "", str),
    "SLACK_TOKEN": ("", "", str),
}

CONSTANCE_CONFIG_FIELDSETS = OrderedDict(
    (
        ("System", ("SYSTEM_USER", "WEEKENDS_DAYS")),
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
    ),
)
