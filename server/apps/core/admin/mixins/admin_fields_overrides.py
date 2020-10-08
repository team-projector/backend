from jnt_django_toolbox.admin.widgets import BitFieldWidget
from jnt_django_toolbox.models.fields import BitField


class AdminFieldsOverridesMixin:
    """A mixin with form fields overrides."""

    formfield_overrides = {
        BitField: {"widget": BitFieldWidget},
    }
