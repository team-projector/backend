from apps.users.models import User
from apps.users.services.user.summary.provider import (
    UserIssuesSummary,
    UserIssuesSummaryProvider,
)


def get_user_issues_summary(user: User, **kwargs) -> UserIssuesSummary:
    """Get user issues summary."""
    return UserIssuesSummaryProvider(user, **kwargs).get_summary()
