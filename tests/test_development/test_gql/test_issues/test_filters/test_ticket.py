import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.graphql.fields.issues import IssuesFilterSet
from apps.development.models.issue import Issue
from apps.users.models import User
from tests.test_development.factories import IssueFactory, TicketFactory


def test_by_ticket(user, auth_rf):
    """
    Test by ticket.

    :param user:
    :param auth_rf:
    """
    user.roles.MANAGER = True
    user.save()

    ticket = TicketFactory.create()
    IssueFactory.create_batch(3, user=user, ticket=ticket)
    IssueFactory.create_batch(2, user=user, ticket=TicketFactory.create())

    issues = IssuesFilterSet(
        data={"ticket": ticket.pk},
        queryset=Issue.objects.all(),
        request=auth_rf.get("/"),
    ).qs

    assert issues.count() == 3
    assert all(issue.ticket == ticket for issue in issues)


def test_not_project_manager(user, auth_rf):
    """
    Test not project manager.

    :param user:
    :param auth_rf:
    """
    user.roles = User.roles.DEVELOPER
    user.save()

    ticket = TicketFactory.create()
    IssueFactory.create_batch(3, user=user, ticket=ticket)

    with pytest.raises(GraphQLPermissionDenied):
        IssuesFilterSet(  # noqa: WPS428
            data={"ticket": ticket.pk},
            queryset=Issue.objects.all(),
            request=auth_rf.get("/"),
        ).qs
