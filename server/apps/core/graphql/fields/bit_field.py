# -*- coding: utf-8 -*-

import graphene
from graphene_django.converter import convert_django_field
from jnt_django_toolbox.models.fields import BitField as ModelBitField


class BitField(graphene.Scalar):
    """Bit field."""

    @staticmethod
    def serialize(bit):  # noqa: WPS602
        """Serialize."""
        return [key for key, setted in bit if setted]


@convert_django_field.register(ModelBitField)
def convert_field_to_float(field, registry=None):
    """Field to float."""
    return graphene.Field(
        BitField, description=field.help_text, required=not field.null,
    )
