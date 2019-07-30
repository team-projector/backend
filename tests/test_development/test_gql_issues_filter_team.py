from apps.development.models import TeamMember
from apps.development.graphql.types.issue import IssueType
from apps.development.models import Issue
from apps.development.graphql.filters import IssuesFilterSet
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_development.factories_gitlab import AttrDict
from tests.test_users.factories import UserFactory


def test_one_member(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    IssueFactory.create_batch(2, user=user)

    another_user = UserFactory.create()
    IssueFactory.create_batch(3, user=another_user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'team': team.id},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 2


def test_many_members(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    IssueFactory.create_batch(2, user=user)

    another_user = UserFactory.create()
    IssueFactory.create_batch(3, user=another_user)

    TeamMemberFactory.create(
        user=another_user,
        team=team,
        roles=TeamMember.roles.developer
    )

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'team': team.id},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 5


def test_many_teams(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    another_user = UserFactory.create()

    IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(3, user=another_user)

    another_team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=another_team,
        roles=TeamMember.roles.watcher
    )

    TeamMemberFactory.create(
        user=another_user,
        team=another_team,
        roles=TeamMember.roles.developer
    )

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'team': team.id},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 2
