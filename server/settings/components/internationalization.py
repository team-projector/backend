import os

from django.utils.translation import gettext_lazy as _

from server.settings.components.paths import PROJECT_ROOT

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True

USE_TZ = True

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('MESSAGE__ENGLISH')),
]

LOCALE_PATHS = [os.path.join(PROJECT_ROOT, 'locale')]
