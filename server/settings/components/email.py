EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''  # noqa S105
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = DEFAULT_FROM_EMAIL
