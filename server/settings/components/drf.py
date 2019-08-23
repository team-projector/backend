REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.core.api.authentication.TokenAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'NON_FIELD_ERRORS_KEY': 'detail',
    'DEFAULT_PAGINATION_CLASS': 'apps.core.api.pagination.DefaultPagination',
    'PAGE_SIZE': 20,
    'SEARCH_PARAM': 'q',
    'COERCE_DECIMAL_TO_STRING': False
}

REST_FRAMEWORK_TOKEN_EXPIRE = 60 * 24 * 30  # mins
