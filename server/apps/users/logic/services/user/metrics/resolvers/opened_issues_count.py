from apps.development.models import Issue
from apps.development.models.issue import IssueState
from apps.users.models import User


def opened_issues_count_resolver(user: User):
    """Get user's opened issues count."""
    return Issue.objects.filter(
        user=user,
        state=IssueState.OPENED,
    ).count()
