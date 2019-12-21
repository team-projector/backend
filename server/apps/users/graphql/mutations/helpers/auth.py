# -*- coding: utf-8 -*-

from django.http import HttpRequest
from social_django.compat import reverse
from social_django.utils import load_backend, load_strategy
from social_django.views import NAMESPACE


def page_social_auth(request: HttpRequest) -> HttpRequest:
    """Page social auth."""
    uri = reverse('{0}:complete'.format(NAMESPACE), args=('gitlab',))
    request.social_strategy = load_strategy(request)

    request.strategy = getattr(
        request,
        'strategy',
        request.social_strategy,
    )

    request.backend = load_backend(
        request.social_strategy,
        'gitlab',
        uri,
    )

    return request
