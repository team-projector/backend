# -*- coding: utf-8 -*-

from typing import Dict

import graphene
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
    def mutate(cls, root, info, **kwargs):  # noqa WPS110
        """Mutate."""
        cls.check_premissions(root, info, **kwargs)

        return cls.do_mutate(root, info, **kwargs)

    @classmethod
    def check_premissions(cls, root, info, **kwargs) -> None:  # noqa WPS110
        """Check premissions."""
        if not cls.has_permission(root, info, **kwargs):
            raise PermissionDenied()

    @classmethod
    def do_mutate(cls, root, info, **kwargs) -> None:  # noqa WPS110
        """Method should be implemente in subclass."""
        raise NotImplementedError


class ArgumentsValidationMixin(BaseMutation):
    """A Mixin validates input fields in mutations."""

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa WPS110
        """Do mutate."""
        form = cls.form_class(data=kwargs)

        if not form.is_valid():
            raise ValidationError(form.errors)

        return cls.perform_mutate(info, form.cleaned_data)

    @classmethod
    def perform_mutate(cls, info, cleaned_data: Dict) -> None:  # noqa WPS110
        """Method should be implemente in subclass."""
        raise NotImplementedError
