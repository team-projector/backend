# -*- coding: utf-8 -*-

from pytest import raises

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models.issue import Issue
from tests.test_development.factories import IssueFactory, TicketFactory


def test_by_ticket(user, auth_rf):
    user.roles.PROJECT_MANAGER = True
    user.save()

    ticket = TicketFactory.create()
    IssueFactory.create_batch(3, user=user, ticket=ticket)
    IssueFactory.create_batch(2, user=user, ticket=TicketFactory.create())

    results = IssuesFilterSet(
        data={"ticket": ticket.pk},
        queryset=Issue.objects.all(),
        request=auth_rf.get("/")
    ).qs

    assert results.count() == 3
    assert all(item.ticket == ticket for item in results)


def test_not_project_manager(user, auth_rf):
    ticket = TicketFactory.create()
    IssueFactory.create_batch(3, user=user, ticket=ticket)

    with raises(GraphQLPermissionDenied):
        IssuesFilterSet(  # noqa: WPS428
            data={"ticket": ticket.pk},
            queryset=Issue.objects.all(),
            request=auth_rf.get("/")
        ).qs
