from graphql import ResolveInfo

from apps.core.graphql.security.authentication import auth_required
from apps.users.models import User
from apps.users.services.user.summary.provider import UserIssuesSummary
from apps.users.services.user.summary.issues import (
    get_user_issues_summary,
)


def resolve_user_issues_summary(
    parent: User,
    info: ResolveInfo,  # noqa: WPS110
    **kwargs,
) -> UserIssuesSummary:
    """Get issue summary for user."""
    auth_required(info)

    return get_user_issues_summary(parent, **kwargs)
