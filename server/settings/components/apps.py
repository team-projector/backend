INSTALLED_APPS = (
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
    'django_extensions',
    'django_filters',
    'rest_framework',
    'rest_framework_swagger',
    'corsheaders',
    'admin_auto_filters',
    'social_django',

    # apps
    'apps.core',
    'apps.users',
    'apps.development',
    'apps.payroll',
)
