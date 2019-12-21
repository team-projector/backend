# -*- coding: utf-8 -*-

from typing import Optional

import graphene
from graphql import ResolveInfo
from rest_framework.exceptions import PermissionDenied

from apps.core.graphql.security.mixins.mutation import AuthMutation
from apps.core.graphql.security.permissions import AllowAuthenticated


class NoInputMutation(AuthMutation, graphene.Mutation):
    permission_classes = (AllowAuthenticated,)

    class Meta:
        abstract = True

    @classmethod
    def mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
    ):
        cls.check_premissions(root, info)

        return cls.perform_mutate(root, info)

    @classmethod
    def check_premissions(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
    ) -> None:
        if not cls.has_permission(root, info):
            raise PermissionDenied()

    @classmethod
    def perform_mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
    ) -> 'NoInputMutation':
        raise NotImplementedError
