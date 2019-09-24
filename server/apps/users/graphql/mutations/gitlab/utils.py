# -*- coding: utf-8 -*-

from django.http import Http404, HttpRequest
from social_core.exceptions import MissingBackend
from social_django.compat import reverse
from social_django.utils import load_strategy, load_backend
from social_django.views import NAMESPACE


def psa(request: HttpRequest) -> HttpRequest:
    uri = reverse(f'{NAMESPACE}:complete', args=('gitlab',))
    request.social_strategy = load_strategy(request)

    request.strategy = getattr(
        request,
        'strategy',
        request.social_strategy,
    )

    try:
        request.backend = load_backend(
            request.social_strategy,
            'gitlab',
            uri,
        )
    except MissingBackend:
        raise Http404('Backend not found')

    return request
