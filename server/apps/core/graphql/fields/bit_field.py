# -*- coding: utf-8 -*-

import graphene
from bitfield import BitField as ModelBitField
from graphene_django.converter import convert_django_field


class BitField(graphene.Scalar):
    """Bit field."""

    @staticmethod # noqa WPS602
    def serialize(vals):
        """Serialize."""
        return [
            val
            for val, setted in vals
            if setted
        ]

    @staticmethod # noqa WPS602
    def parse_literal(node):
        """Parse literal."""
        # TODO implement
        return str(node)

    @staticmethod # noqa WPS602
    def parse_value(value):
        """Parse value."""
        # TODO implement
        return value


@convert_django_field.register(ModelBitField)
def convert_field_to_float(field, registry=None):
    """Field to float."""
    return graphene.Field(
        BitField,
        description=field.help_text,
        required=not field.null,
    )
