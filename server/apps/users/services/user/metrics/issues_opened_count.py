from apps.core.graphql.security.authentication import auth_required
from apps.development.models import Issue
from apps.development.models.issue import IssueState


def issues_opened_count_resolver(parent, info, **kwargs) -> int:  # noqa:WPS110
    """:returns user opened issues count."""
    auth_required(info)

    user = info.context.user

    if user.is_authenticated:
        return Issue.objects.filter(
            user=user,
            state=IssueState.OPENED,
        ).count()

    return 0
