# -*- coding: utf-8 -*-

INSTALLED_APPS = (
    "jnt_admin_tools",
    "jnt_admin_tools.theming",
    "jnt_admin_tools.menu",
    "jnt_admin_tools.dashboard",
    # Default django apps:
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # django-admin:
    "django.contrib.admin",
    "django.contrib.admindocs",
    # vendors
    "jnt_django_toolbox",
    "graphene_django",
    "django_extensions",
    "django_filters",
    "rest_framework",
    "corsheaders",
    "social_django",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "actstream",
    # apps
    "apps.core",
    "apps.users",
    "apps.development",
    "apps.payroll",
)
