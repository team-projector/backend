PROJECT_APPS = [
    'apps.core',
    'apps.users',
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
]

INSTALLED_APPS = VENDOR_APPS + DJANGO_APPS + PROJECT_APPS
