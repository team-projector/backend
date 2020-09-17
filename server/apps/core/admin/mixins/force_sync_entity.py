# -*- coding: utf-8 -*-

from django.contrib.admin.options import BaseModelAdmin
from django.http import HttpResponseRedirect


class ForceSyncEntityMixin(BaseModelAdmin):
    """A mixin shows "Force sync" button on change form page."""

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        Show button on change form page.

        Extra context passes to "submit_line.html" template.
        """
        extra_context = extra_context or {}
        extra_context["show_force_sync"] = True

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def response_change(self, request, instance):
        """Handling "_force_sync"."""
        if "_force_sync" in request.POST:
            self._sync_obj(request, instance)
            return HttpResponseRedirect(request.path)

        return super().response_change(request, instance)

    def sync_handler(self, instance) -> None:
        """Handler should be implemented in child class."""
        raise NotImplementedError

    def _sync_obj(self, request, instance) -> None:
        """
        Sync obj.

        :param request:
        :param instance:
        :rtype: None
        """
        self.sync_handler(instance)
        self.message_user(
            request,
            "{0} '{1}' is syncing".format(
                instance._meta.verbose_name,  # noqa: WPS437
                instance,
            ),
        )
