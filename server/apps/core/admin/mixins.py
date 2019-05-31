from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from django.contrib.admin.options import BaseModelAdmin
from django.http import HttpResponseRedirect


class AdminFormFieldsOverridesMixin:
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }


class ForceSyncEntityMixin(BaseModelAdmin):
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_force_sync'] = True
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def response_change(self, request, obj):
        if '_force_sync' in request.POST:
            self._sync_obj(request, obj)
            return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)

    def _sync_obj(self, request, obj):
        self.sync_handler(obj)
        self.message_user(request, f'{obj._meta.verbose_name} "{obj}" is syncing')

    def sync_handler(self, obj):
        raise NotImplementedError
