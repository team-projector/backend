REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.core.rest.expiring_token.ExpiringTokenAuthentication'
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'NON_FIELD_ERRORS_KEY': 'detail',
    'DEFAULT_PAGINATION_CLASS': 'apps.core.rest.pagination.DefaultPagination',
    'PAGE_SIZE': 20,
    'SEARCH_PARAM': 'q'
}

REST_FRAMEWORK_TOKEN_EXPIRE_MINUTES = 60 * 24
