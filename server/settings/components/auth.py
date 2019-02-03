AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

AUTH_USER_MODEL = 'users.User'

ACCOUNT_USER_MODEL_USERNAME_FIELD = 'login'

AUTHENTICATION_BACKENDS = [
    'apps.core.gitlab.auth.CustomGitLabOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

SOCIAL_AUTH_USER_MODEL = 'users.User'
