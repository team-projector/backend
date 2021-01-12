from django.contrib.auth.models import AnonymousUser
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied


def auth_required(info: ResolveInfo) -> None:  # noqa: WPS110
    """Check user is auth."""
    user = getattr(info.context, "user", None) or AnonymousUser
    if not user.is_active:
        raise GraphQLPermissionDenied()
