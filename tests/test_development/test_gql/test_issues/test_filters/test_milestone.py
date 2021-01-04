import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.graphql.fields.issues import IssuesFilterSet
from apps.development.models.issue import Issue
from apps.users.models import User
from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
)


def test_filter_by_milestone(user, auth_rf):
    """
    Test filter by milestone.

    :param user:
    :param auth_rf:
    """
    user.roles.MANAGER = True
    user.save()

    milestone = ProjectMilestoneFactory.create()
    IssueFactory.create_batch(3, user=user, milestone=milestone)

    IssueFactory.create_batch(
        2,
        user=user,
        milestone=ProjectMilestoneFactory.create(),
    )

    queryset = IssuesFilterSet(
        data={"milestone": milestone.pk},
        queryset=Issue.objects.all(),
        request=auth_rf.get("/"),
    ).qs

    assert queryset.count() == 3
    assert all(issue.milestone == milestone for issue in queryset)


def test_not_project_manager(user, auth_rf):
    """
    Test not project manager.

    :param user:
    :param auth_rf:
    """
    user.roles = User.roles.DEVELOPER
    user.save()

    milestone = ProjectMilestoneFactory.create()
    IssueFactory.create_batch(3, user=user, milestone=milestone)

    with pytest.raises(GraphQLPermissionDenied):
        IssuesFilterSet(  # noqa: WPS428
            data={"milestone": milestone.pk},
            queryset=Issue.objects.all(),
            request=auth_rf.get("/"),
        ).qs
