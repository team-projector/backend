# -*- coding: utf-8 -*-

from typing import Dict
from urllib.parse import urlencode

from admin_tools.mixins import AdminAutocompleteFieldsMixin
from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import redirect

from apps.core.admin.mixins import AdminFieldsOverridesMixin


class BaseModelAdmin(
    AdminAutocompleteFieldsMixin,
    AdminFieldsOverridesMixin,
    admin.ModelAdmin,
):
    """A base class for admin dashboard."""

    list_per_page = 20

    class Media:
        """Media."""

    def changelist_view(self, request: HttpRequest, extra_context=None):
        ref = request.META.get('HTTP_REFERER', '')
        path = request.META.get('PATH_INFO', '')

        if request.GET or (ref and ref.endswith(path)):
            return super().changelist_view(
                request,
                extra_context=extra_context,
            )

        default_filters = self.get_default_filters(request)
        if default_filters:
            query = urlencode(default_filters)
            return redirect('{0}?{1}'.format(path, query))

    def get_default_filters(self, request: HttpRequest) -> Dict[str, str]:
        """Set default filters to the page."""
