# -*- coding: utf-8 -*-

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

AUTH_USER_MODEL = 'users.User'

ACCOUNT_USER_MODEL_USERNAME_FIELD = 'login'

AUTHENTICATION_BACKENDS = [
    'apps.core.auth.backends.GitLabOAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'admin:login'

SOCIAL_AUTH_USER_MODEL = 'users.User'
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_GITLAB_KEY = None
SOCIAL_AUTH_GITLAB_SECRET = None
SOCIAL_AUTH_GITLAB_REDIRECT_URI = None

TOKEN_EXPIRE_DAYS = 30
TOKEN_EXPIRE_PERIOD = 60 * 24 * TOKEN_EXPIRE_DAYS  # mins
