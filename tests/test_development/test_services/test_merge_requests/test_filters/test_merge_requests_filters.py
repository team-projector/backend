# -*- coding: utf-8 -*-

from apps.development.graphql.filters import MergeRequestFilterSet
from apps.development.models import MergeRequest, TeamMember
from apps.development.models.merge_request import MergeRequestState
from tests.test_development.factories import (
    MergeRequestFactory,
    ProjectFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories.user import UserFactory


def test_filter_by_user(user):
    user_2 = UserFactory.create()

    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user, team=team, roles=TeamMember.roles.LEADER
    )

    TeamMemberFactory.create(
        user=user_2, team=team, roles=TeamMember.roles.DEVELOPER
    )

    MergeRequestFactory.create(user=user_2)
    MergeRequestFactory.create_batch(3, user=user)

    results = MergeRequestFilterSet(
        data={"user": user_2.id}, queryset=MergeRequest.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().user == user_2

    results = MergeRequestFilterSet(
        data={"user": user.id}, queryset=MergeRequest.objects.all(),
    ).qs

    assert results.count() == 3


def test_filter_by_state(user):
    merge_request_opened = MergeRequestFactory.create(
        user=user, state=MergeRequestState.OPENED
    )
    merge_request_closed = MergeRequestFactory.create(
        user=user, state=MergeRequestState.CLOSED
    )

    results = MergeRequestFilterSet(
        data={"state": MergeRequestState.CLOSED},
        queryset=MergeRequest.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first() == merge_request_closed

    results = MergeRequestFilterSet(
        data={"state": MergeRequestState.OPENED},
        queryset=MergeRequest.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first() == merge_request_opened


def test_filter_by_projects(user):
    project_1 = ProjectFactory.create()
    MergeRequestFactory.create(user=user, project=project_1)

    project_2 = ProjectFactory.create()
    MergeRequestFactory.create(user=user, project=project_2)

    MergeRequestFactory.create_batch(
        3, user=user, project=ProjectFactory.create()
    )

    results = MergeRequestFilterSet(
        data={"project": project_1.id}, queryset=MergeRequest.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().project == project_1

    results = MergeRequestFilterSet(
        data={"project": project_2.id}, queryset=MergeRequest.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().project == project_2


def test_ordering(user):
    merge_request_1 = MergeRequestFactory.create(title="agent", user=user)
    merge_request_2 = MergeRequestFactory.create(title="cloud", user=user)
    merge_request_3 = MergeRequestFactory.create(title="bar", user=user)

    results = MergeRequestFilterSet(
        data={"order_by": "title"}, queryset=MergeRequest.objects.all(),
    ).qs

    assert list(results) == [merge_request_1, merge_request_3, merge_request_2]

    results = MergeRequestFilterSet(
        data={"order_by": "-title"}, queryset=MergeRequest.objects.all(),
    ).qs

    assert list(results) == [merge_request_2, merge_request_3, merge_request_1]
