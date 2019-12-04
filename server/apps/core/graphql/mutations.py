# -*- coding: utf-8 -*-

from typing import Dict

import graphene
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene_django.rest_framework.serializer_converter import (
    get_graphene_type_from_serializer_field,
)
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.core.graphql.security.mixins.mutation import AuthMutation
from apps.core.graphql.security.permissions import AllowAuthenticated


class BaseMutation(
    AuthMutation,
    graphene.Mutation,
):
    """A base class mutation."""

    permission_classes = (AllowAuthenticated,)

    class Meta:
        abstract = True

    @classmethod
    def mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Mutate."""
        cls.check_premissions(root, info, **kwargs)

        return cls.do_mutate(root, info, **kwargs)

    @classmethod
    def check_premissions(cls, root, info, **kwargs) -> None:  # noqa: WPS110
        """Check premissions."""
        if not cls.has_permission(root, info, **kwargs):
            raise PermissionDenied()

    @classmethod
    def do_mutate(cls, root, info, **kwargs) -> None:  # noqa: WPS110
        """Method should be implemente in subclass."""
        raise NotImplementedError


class RestrictedAccessSerializerMutation(
    AuthMutation,
    SerializerMutation,
):
    """A base class for mutations requiring restricted access."""

    class Meta:
        abstract = True

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):  # noqa: WPS110
        """Mutates object and returns a payload."""
        if not cls.has_permission(root, info, **input):
            raise PermissionDenied()

        return super().mutate_and_get_payload(root, info, **input)


class ArgumentsValidationMixin(BaseMutation):
    """A Mixin validates input fields in mutations."""

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Do mutate."""
        form = cls.form_class(data=kwargs)

        if not form.is_valid():
            raise ValidationError(form.errors)

        return cls.perform_mutate(info, form.cleaned_data)

    @classmethod
    def perform_mutate(cls, info, cleaned_data: Dict) -> None:  # noqa: WPS110
        """Method should be implemente in subclass."""
        raise NotImplementedError


@get_graphene_type_from_serializer_field.register(serializers.ManyRelatedField)
def convert_list_serializer_to_field(field):
    """Defines graphql field type for serializers.ManyRelatedField."""
    return (graphene.List, graphene.String)
