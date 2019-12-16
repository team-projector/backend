# -*- coding: utf-8 -*-

import graphene
from graphene_django.rest_framework.serializer_converter import (
    get_graphene_type_from_serializer_field,
)
from rest_framework import serializers


@get_graphene_type_from_serializer_field.register(serializers.ManyRelatedField)
def convert_list_serializer_to_field(field):
    """Defines graphql field type for serializers.ManyRelatedField."""
    return (graphene.List, graphene.ID)


@get_graphene_type_from_serializer_field.register(
    serializers.PrimaryKeyRelatedField
)
def convert_serializer_field_to_id(field):
    """Defines graphql field type for serializers.ManyRelatedField."""
    return graphene.ID
