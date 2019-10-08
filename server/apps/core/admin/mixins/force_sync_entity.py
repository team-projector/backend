# -*- coding: utf-8 -*-

from django.contrib.admin.options import BaseModelAdmin
from django.http import HttpResponseRedirect


class ForceSyncEntityMixin(BaseModelAdmin):
    """A mixin shows "Force sync" button on change form page."""

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Show button on change form page.

        Extra context passes to "submit_line.html" template.
        """
        extra_context = extra_context or {}
        extra_context['show_force_sync'] = True

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def response_change(self, request, obj):
        """Handling "_force_sync"."""
        if '_force_sync' in request.POST:
            self._sync_obj(request, obj)
            return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)

    def sync_handler(self, obj):
        """Handler should be implemented in child class."""
        raise NotImplementedError

    def _sync_obj(self, request, obj):
        self.sync_handler(obj)
        self.message_user(
            request,
            f'{obj._meta.verbose_name} "{obj}" is syncing',
        )
