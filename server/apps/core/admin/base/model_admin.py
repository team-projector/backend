from typing import Dict
from urllib.parse import urlencode, urlparse

from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import redirect
from jnt_admin_tools.mixins import (
    AdminAutocompleteFieldsMixin,
    AdminClickableLinksMixin,
)

from apps.core.admin.mixins import AdminFieldsOverridesMixin


class BaseModelAdmin(  # noqa: WPS215
    AdminAutocompleteFieldsMixin,
    AdminFieldsOverridesMixin,
    AdminClickableLinksMixin,
    admin.ModelAdmin,
):
    """A base class for admin dashboard."""

    class Media:
        """Media."""

    list_per_page = 20

    def changelist_view(self, request: HttpRequest, extra_context=None):
        """The "change list" admin view for this model."""
        if self._need_apply_default_filters(request):
            return redirect(
                "{0}?{1}".format(
                    request.META.get("PATH_INFO"),
                    urlencode(self.get_default_filters(request)),
                ),
            )

        return super().changelist_view(request, extra_context=extra_context)

    def get_default_filters(self, request: HttpRequest) -> Dict[str, str]:
        """Set default filters to the page."""

    def _need_apply_default_filters(self, request) -> bool:
        has_query = bool(request.META.get("QUERY_STRING"))
        has_default = bool(self.get_default_filters(request))
        is_get_request = request.method == "GET"
        from_another_url = self._get_referer_path(request) != request.META.get(
            "PATH_INFO",
            "",
        )

        return all(
            (
                has_default,
                is_get_request,
                from_another_url,
                not has_query,
            ),
        )

    def _get_referer_path(self, request) -> str:
        return urlparse(request.META.get("HTTP_REFERER", "")).path
