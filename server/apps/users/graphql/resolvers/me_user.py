from typing import Optional

from graphql import ResolveInfo

from apps.core.graphql.security.authentication import auth_required


def resolve_me_user(root: Optional[object], info: ResolveInfo):  # noqa: WPS110
    """Resolve me user."""
    auth_required(info)

    return info.context.user  # type: ignore
