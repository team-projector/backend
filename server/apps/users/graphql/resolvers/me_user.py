from typing import Optional

from graphql import ResolveInfo


def resolve_me_user(root: Optional[object], info: ResolveInfo):  # noqa: WPS110
    """Resolve me user."""
    return info.context.user  # type: ignore
