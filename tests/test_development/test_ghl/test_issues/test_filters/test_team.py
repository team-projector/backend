from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models import TeamMember
from apps.development.models.issue import Issue
from tests.test_development.factories import (
    IssueFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories.user import UserFactory


def test_by_team_with_one_member(user):
    """
    Test by team with one member.

    :param user:
    """
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER,
    )

    IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(5, user=UserFactory.create())

    queryset = IssuesFilterSet(
        data={"team": team.id},
        queryset=Issue.objects.all(),
    ).qs

    assert queryset.count() == 2
    assert all(issue.user == user for issue in queryset)


def test_by_team_with_many_members(user):
    """
    Test by team with many members.

    :param user:
    """
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER,
    )
    IssueFactory.create_batch(2, user=user)

    another_user = UserFactory.create()
    IssueFactory.create_batch(3, user=another_user)

    TeamMemberFactory.create(
        user=another_user,
        team=team,
        roles=TeamMember.roles.DEVELOPER,
    )

    IssueFactory.create_batch(4, user=UserFactory.create())

    queryset = IssuesFilterSet(
        data={"team": team.id},
        queryset=Issue.objects.all(),
    ).qs

    assert queryset.count() == 5
    assert all(issue.user in {user, another_user} for issue in queryset)


def test_by_team_with_watcher(user):
    """
    Test by team with watcher.

    :param user:
    """
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER,
    )
    IssueFactory.create_batch(2, user=user)

    another_user = UserFactory.create()
    IssueFactory.create_batch(3, user=another_user)

    another_team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=another_team,
        roles=TeamMember.roles.WATCHER,
    )

    TeamMemberFactory.create(
        user=another_user,
        team=another_team,
        roles=TeamMember.roles.DEVELOPER,
    )

    queryset = IssuesFilterSet(
        data={"team": team.id},
        queryset=Issue.objects.all(),
    ).qs

    assert queryset.count() == 2
    assert all(issue.user == user for issue in queryset)

    queryset = IssuesFilterSet(
        data={"team": another_team.id},
        queryset=Issue.objects.all(),
    ).qs

    assert queryset.count() == 3
    assert all(issue.user == another_user for issue in queryset)
