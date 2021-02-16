from apps.development.models import MergeRequest
from apps.development.models.issue import IssueState
from apps.users.models import User


def opened_merge_requests_count_resolver(user: User):
    """Get user's opened merge requests count."""
    return MergeRequest.objects.filter(
        user=user,
        state=IssueState.OPENED,
    ).count()
