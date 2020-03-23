# -*- coding: utf-8 -*-

from apps.development.graphql.filters import MergeRequestFilterSet
from apps.development.models import MergeRequest, TeamMember
from apps.development.models.merge_request import MergeRequestState
from tests.helpers import lists
from tests.test_development.factories import (
    MergeRequestFactory,
    ProjectFactory,
    TeamFactory,
    TeamMemberFactory,
)


def test_filter_by_user(team_leader, team_developer):
    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=team_leader, team=team, roles=TeamMember.roles.LEADER,
    )

    TeamMemberFactory.create(
        user=team_developer, team=team, roles=TeamMember.roles.DEVELOPER,
    )

    MergeRequestFactory.create(user=team_developer)
    MergeRequestFactory.create_batch(3, user=team_leader)

    results = MergeRequestFilterSet(
        data={"user": team_developer.pk}, queryset=MergeRequest.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().user == team_developer

    results = MergeRequestFilterSet(
        data={"user": team_leader.pk}, queryset=MergeRequest.objects.all(),
    ).qs

    assert results.count() == 3


def test_filter_by_state(user):
    merge_request_opened = MergeRequestFactory.create(
        user=user, state=MergeRequestState.OPENED,
    )
    merge_request_closed = MergeRequestFactory.create(
        user=user, state=MergeRequestState.CLOSED,
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
    projects = ProjectFactory.create_batch(2)
    MergeRequestFactory.create(user=user, project=projects[0])
    MergeRequestFactory.create(user=user, project=projects[1])

    MergeRequestFactory.create_batch(
        3, user=user, project=ProjectFactory.create(),
    )

    results = MergeRequestFilterSet(
        data={"project": projects[0].id}, queryset=MergeRequest.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().project == projects[0]

    results = MergeRequestFilterSet(
        data={"project": projects[1].id}, queryset=MergeRequest.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().project == projects[1]


def test_ordering(user):
    merge_requests = [
        MergeRequestFactory.create(title=title, user=user)
        for title in ("agent", "cloud", "bar")
    ]

    results = MergeRequestFilterSet(
        data={"order_by": "title"}, queryset=MergeRequest.objects.all(),
    ).qs
    assert list(results) == lists.sub_list(merge_requests, (0, 2, 1))


def test_ordering_desc(user):
    merge_requests = [
        MergeRequestFactory.create(title=title, user=user)
        for title in ("agent", "cloud", "bar")
    ]

    results = MergeRequestFilterSet(
        data={"order_by": "-title"}, queryset=MergeRequest.objects.all(),
    ).qs
    assert list(results) == lists.sub_list(merge_requests, (1, 2, 0))
