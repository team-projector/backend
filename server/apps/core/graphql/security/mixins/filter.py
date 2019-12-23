# -*- coding: utf-8 -*-

from typing import Optional

from graphene_django.filter import DjangoFilterConnectionField
from graphql import ResolveInfo

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.core.graphql.security.permissions import AllowAny


class AuthFilter(DjangoFilterConnectionField):
    """Custom ConnectionField for permission system."""

    permission_classes = (AllowAny,)

    @classmethod
    def connection_resolver(  # noqa: WPS211
        cls,
        resolver,
        connection,
        default_manager,
        queryset_resolver,
        max_limit,
        enforce_first_or_last,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **args,
    ):
        """Check if user has permissions."""
        if not cls.has_permission(info):
            raise GraphQLPermissionDenied()

        return super(  # noqa: WPS608
            DjangoFilterConnectionField,
            cls,
        ).connection_resolver(
            resolver,
            connection,
            default_manager,
            queryset_resolver,
            max_limit,
            enforce_first_or_last,
            root,
            info,
            **args,
        )

    @classmethod
    def has_permission(
        cls,
        info: ResolveInfo,  # noqa: WPS110
    ) -> bool:
        """Check if user has permissions."""
        return all(
            perm().has_filter_permission(info)
            for perm in cls.permission_classes
        )
