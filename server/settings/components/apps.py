# -*- coding: utf-8 -*-

INSTALLED_APPS = (

    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',

    # Default django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # django-admin:

    'django.contrib.admin',
    'django.contrib.admindocs',

    # vendors
    'graphene_django',
    'django_extensions',
    'django_filters',
    'rest_framework',
    'corsheaders',
    'social_django',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'actstream',

    # apps
    'apps.core',
    'apps.users',
    'apps.development',
    'apps.payroll',
)
