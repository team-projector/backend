import calendar

from decouple import config

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

# TODO: remove after merge #492
GITLAB_ADDRESS = config("DJANGO_GITLAB_ADDRESS", default="https://gitlab.com")
GITLAB_NO_SYNC = config("DJANGO_GITLAB_NO_SYNC", default=False, cast=bool)

GITLAB_WEBHOOK_SECRET_TOKEN = config(
    "DJANGO_WEBHOOK_SECRET_TOKEN", default="",
)

GITLAB_CHECK_WEBHOOKS = config(
    "DJANGO_GITLAB_CHECK_WEBHOOKS", default=False, cast=bool,
)

SLACK_TOKEN = config("DJANGO_SLACK_TOKEN", default="")

TP_WEEKENDS_DAYS = (calendar.SATURDAY, calendar.SUNDAY)
TP_SYSTEM_USER_LOGIN = "system"

GITLAB_TOKEN = config("DJANGO_GITLAB_TOKEN", default="")
# end of TODO

CONSTANCE_ADDITIONAL_FIELDS = {
    "weekend_days": [
        "django.forms.MultipleChoiceField",
        {
            "required": True,
            "choices": [(getattr(calendar, day), day) for day in WEEK_DAYS],
        },
    ],
}

# TODO: rename to CONSTANCE_CONFIG after merge #492
CONSTANCE_CONFIG_AFTER_MERGE = {
    "TP_WEEKENDS_DAYS": (
        (calendar.SATURDAY, calendar.SUNDAY),
        "",
        "weekend_days",
    ),
    "SYSTEM_USER": ("system", "", str),
    "GITLAB_ADDRESS": ("https://gitlab.com", "", str),
    "GITLAB_SYNC": (True, "", bool),  # make it to "GITLAB_SYNC":True
    "GITLAB_TOKEN": ("", "", str),
    "GITLAB_WEBHOOK_SECRET_TOKEN": ("", "", str),
    "GITLAB_CHECK_WEBHOOKS": (False, "", bool),
    "SLACK_TOKEN": ("", "", str),
}

CONSTANCE_CONFIG = {
    "WEEKENDS_DAYS": (TP_WEEKENDS_DAYS, "", "weekend_days"),
    "SYSTEM_USER": (TP_SYSTEM_USER_LOGIN, "", str),
    "GITLAB_ADDRESS": (GITLAB_ADDRESS, "", str),
    "GITLAB_SYNC": (not GITLAB_NO_SYNC, "", bool),
    "GITLAB_TOKEN": (GITLAB_TOKEN, "", str),
    "GITLAB_WEBHOOK_SECRET_TOKEN": (GITLAB_WEBHOOK_SECRET_TOKEN, "", str),
    "GITLAB_CHECK_WEBHOOKS": (GITLAB_CHECK_WEBHOOKS, "", bool),
    "SLACK_TOKEN": (SLACK_TOKEN, "", str),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "System": ("SYSTEM_USER", "WEEKENDS_DAYS"),
    "Gitlab": (
        "GITLAB_ADDRESS",
        "GITLAB_SYNC",
        "GITLAB_TOKEN",
        "GITLAB_WEBHOOK_SECRET_TOKEN",
        "GITLAB_CHECK_WEBHOOKS",
    ),
    "Notifications": ("SLACK_TOKEN",),
}
