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
    'django_extensions',
    'django_filters',
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    'admin_auto_filters',
    'social_django',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',

    # apps
    'apps.core',
    'apps.users',
    'apps.development',
    'apps.payroll',
)
