# -*- coding: utf-8 -*-

from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.core.graphql.errors import GraphQLNotFound


def get_object_or_not_found(queryset, *filter_args, **filter_kwargs):
    """Same as Django's standard shortcut, but with GraphQLNotFound."""
    try:
        return get_object_or_404(queryset, *filter_args, **filter_kwargs)
    except Http404:
        raise GraphQLNotFound()
