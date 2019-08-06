from apps.development.models import Issue, TeamMember
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_users.factories import UserFactory


def test_by_assignee(user):
    another_user = UserFactory.create()

    IssueFactory.create_batch(4, user=user)
    IssueFactory.create_batch(2, user=another_user)

    allowed = Issue.objects.allowed_for_user(user)

    assert allowed.count() == 4


def test_by_team_leader(user):
    leader = UserFactory.create()
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=leader,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.developer
    )

    IssueFactory.create_batch(4, user=user)

    allowed = Issue.objects.allowed_for_user(leader)

    assert allowed.count() == 4


def test_by_team_leader_and_user(user):
    leader = UserFactory.create()
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=leader,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.developer
    )

    IssueFactory.create_batch(4, user=user)
    IssueFactory.create_batch(3, user=leader)

    allowed = Issue.objects.allowed_for_user(leader)

    assert allowed.count() == 7


def test_by_team_watcher(user):
    watcher = UserFactory.create()
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=watcher,
        team=team,
        roles=TeamMember.roles.watcher
    )

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.developer
    )

    IssueFactory.create_batch(4, user=user)

    allowed = Issue.objects.allowed_for_user(watcher)

    assert allowed.count() == 4
