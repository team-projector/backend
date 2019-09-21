from graphene_django.filter import DjangoFilterConnectionField
from graphql import ResolveInfo
from rest_framework.exceptions import PermissionDenied

from apps.core.graphql.security.permissions import AllowAny


class AuthFilter(DjangoFilterConnectionField):
    """
    Custom ConnectionField for permission system.
    """
    permission_classes = (AllowAny,)

    @classmethod
    def has_permission(cls, info: ResolveInfo) -> bool:
        return all(
            (perm().has_filter_permission(info) for perm in
             cls.permission_classes),
        )

    @classmethod
    def connection_resolver(
        cls, resolver, connection, default_manager,
        max_limit, enforce_first_or_last, filterset_class,
        filtering_args, root, info, **args,
    ):
        if not cls.has_permission(info):
            raise PermissionDenied()

        filter_kwargs = {
            k: v
            for k, v in args.items()
            if k in filtering_args
        }

        qs = filterset_class(
            data=filter_kwargs,
            queryset=default_manager.get_queryset(),
        ).qs

        return super(DjangoFilterConnectionField, cls).connection_resolver(
            resolver, connection, qs, max_limit, enforce_first_or_last,
            root, info, **args,
        )
