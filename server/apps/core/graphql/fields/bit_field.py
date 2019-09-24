# -*- coding: utf-8 -*-

import graphene
from bitfield import BitField as ModelBitField
from graphene_django.converter import convert_django_field


class BitField(graphene.Scalar):
    @staticmethod
    def serialize(val):
        return [
            v
            for v, setted in val
            if setted
        ]

    @staticmethod
    def parse_literal(node):
        # TODO implement
        return str(node)

    @staticmethod
    def parse_value(value):
        # TODO implement
        return value


@convert_django_field.register(ModelBitField)
def convert_field_to_float(field, registry=None):
    return graphene.Field(
        BitField,
        description=field.help_text,
        required=not field.null,
    )
