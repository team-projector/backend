PROJECT_APPS = [
    'apps.core',
    'apps.users',
    'apps.development',
    'apps.payroll',
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

VENDOR_APPS = [
    'rest_framework',
    'rest_framework_swagger',
    'corsheaders',
    'admin_auto_filters',
]

INSTALLED_APPS = VENDOR_APPS + DJANGO_APPS + PROJECT_APPS
