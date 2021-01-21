from django.contrib.contenttypes.admin import GenericStackedInline
from jnt_admin_tools.mixins import AutocompleteFieldsAdminMixin

from apps.core.admin.mixins import AdminFieldsOverridesMixin


class BaseGenericStackedInline(
    AutocompleteFieldsAdminMixin,
    AdminFieldsOverridesMixin,
    GenericStackedInline,
):
    """A base class generic stacked inline."""

    extra = 0
    show_change_link = True
