# -*- coding: utf-8 -*-

from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple


class AdminFormFieldsOverridesMixin:
    """
    A mixin with form fields overrides.
    """
    formfield_overrides = {
        BitField: {
            'widget': BitFieldCheckboxSelectMultiple,
        },
    }
