# -*- coding: utf-8 -*-

from apps.development.graphql.filters import TeamMembersFilterSet
from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_users.factories.user import UserFactory


def test_filter_by_role_developer(user):
    _prepare_data()

    queryset = TeamMembersFilterSet(
        data={"roles": "DEVELOPER"}, queryset=TeamMember.objects.all(),
    ).qs

    assert queryset.count() == 2


def test_filter_by_role_leader(user):
    _prepare_data()

    queryset = TeamMembersFilterSet(
        data={"roles": "LEADER"}, queryset=TeamMember.objects.all(),
    ).qs

    assert queryset.count() == 1


def test_filter_by_role_watcher(user):
    _prepare_data()

    queryset = TeamMembersFilterSet(
        data={"roles": "WATCHER"}, queryset=TeamMember.objects.all(),
    ).qs

    assert queryset.count() == 1


def test_filter_by_incorrect_role(user):
    _prepare_data()

    queryset = TeamMembersFilterSet(
        data={"roles": "incorrect value"}, queryset=TeamMember.objects.all(),
    ).qs

    assert queryset.count() == 4


def test_filter_by_none_role(user):
    _prepare_data()

    queryset = TeamMembersFilterSet(
        data={"roles": None}, queryset=TeamMember.objects.all(),
    ).qs

    assert queryset.count() == 4


def _prepare_data():
    users = UserFactory.create_batch(2)
    teams = TeamFactory.create_batch(2)

    TeamMemberFactory.create(
        user=users[0], team=teams[0], roles=TeamMember.roles.LEADER,
    )
    TeamMemberFactory.create(
        user=users[1], team=teams[0], roles=TeamMember.roles.DEVELOPER,
    )

    TeamMemberFactory.create(
        user=users[0], team=teams[1], roles=TeamMember.roles.WATCHER,
    )
    TeamMemberFactory.create(
        user=users[1], team=teams[1], roles=TeamMember.roles.DEVELOPER,
    )
