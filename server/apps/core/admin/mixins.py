from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple


class AdminFormFieldsOverridesMixin:
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }
