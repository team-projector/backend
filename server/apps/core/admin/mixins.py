from django.http import HttpResponseRedirect

from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple


class AdminFormFieldsOverridesMixin:
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }


class ForceSyncEntityMixin:

    def get_verbose_name(self, obj):
        verbose_name = obj._meta.verbose_name
        return verbose_name

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_force_sync'] = True
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def sync_handler(self, obj):
        raise NotImplementedError

    def response_change(self, request, obj):
        # move to separate func
        if '_force_sync' in request.POST:
            self.sync_handler(obj)
            verbose_name = self.get_verbose_name(obj)
            self.message_user(request, f'{verbose_name} "{obj}" is syncing')
            return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)
