# -*- coding: utf-8 -*-

from constance import config
from django.core.mail.backends.smtp import EmailBackend as BaseEmailBackend


class EmailBackend(BaseEmailBackend):
    """A wrapper that manages the SMTP using constance config."""

    def __init__(  # noqa: WPS211
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        use_tls=None,
        fail_silently=False,
        use_ssl=None,
        timeout=None,
        ssl_keyfile=None,
        ssl_certfile=None,
        **kwargs,
    ):
        """Pass configs from constance."""
        super().__init__(
            host=config.EMAIL_HOST,
            port=config.EMAIL_PORT,
            username=config.EMAIL_HOST_USER,
            password=config.EMAIL_HOST_PASSWORD,
            use_tls=config.EMAIL_USE_TLS,
            fail_silently=fail_silently,
            **kwargs,
        )
