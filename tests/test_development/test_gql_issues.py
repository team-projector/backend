from apps.development.models import TeamMember
from apps.development.graphql.types.issue import IssueType
from apps.development.models import Issue
from apps.development.graphql.filters import IssuesFilterSet
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_development.factories_gitlab import AttrDict
from tests.test_users.factories import UserFactory


def test_issue(user):
    issue = IssueFactory.create(user=user)

    info = AttrDict({
        'context': AttrDict({
            'user': user
        })
    })
    node = IssueType().get_node(info, issue.id)

    assert node == issue


def test_all_issues(user):
    IssueFactory.create_batch(5, user=user)

    info = AttrDict({
        'context': AttrDict({
            'user': user
        }),
        'field_asts': [{}],
        'fragments': {},

    })
    issues = IssueType().get_queryset(Issue.objects.all(), info)

    assert issues.count() == 5


def test_show_participants(user):
    user_2 = UserFactory.create()

    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=user_2,
        team=team,
        roles=TeamMember.roles.developer
    )

    issue = IssueFactory.create(user=user_2)

    users = UserFactory.create_batch(size=3)
    issue.participants.set(users)

    info = AttrDict({
        'context': AttrDict({
            'user': user
        }),
        'field_asts': [{}],
        'fragments': {},

    })
    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'user': user_2.id},
        queryset=issues,
        request=AttrDict({
            'user': user
        }),
    ).qs

    assert results.count() == 1
    assert set(
        x.id for x in results.first().participants.all()
    ) == set(x.id for x in users)


def test_show_users(user):
    user_2 = UserFactory.create()

    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=user_2,
        team=team,
        roles=TeamMember.roles.developer
    )

    IssueFactory.create(user=user_2)
    IssueFactory.create(user=user)

    info = AttrDict({
        'context': AttrDict({
            'user': user
        }),
        'field_asts': [{}],
        'fragments': {},

    })
    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        queryset=issues,
        request=AttrDict({
            'user': user
        }),
    ).qs

    assert results.count() == 2
    assert set(x.user.id for x in results) == {user.id, user_2.id}


def test_issues_filter_by_team_empty(user):
    user_1 = UserFactory.create()
    user_2 = UserFactory.create()

    team_1 = TeamFactory.create()
    team_2 = TeamFactory.create()

    team_1.members.set([user_1, user_2])
    team_2.members.add(user_2)

    IssueFactory.create(user=user)

    info = AttrDict({
        'context': AttrDict({
            'user': user
        }),
        'field_asts': [{}],
        'fragments': {},

    })
    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'team': team_1.id},
        queryset=issues,
        request=AttrDict({
            'user': user
        }),
    ).qs

    assert results.count() == 0


def test_issues_filter_by_team_watcher_empty(user):
    user_1 = UserFactory.create()

    team_1 = TeamFactory.create()
    team_2 = TeamFactory.create()

    team_1.members.set([user_1, user])
    team_2.members.add(user)

    TeamMember.objects.filter(
        team=team_1
    ).update(
        roles=TeamMember.roles.watcher
    )

    IssueFactory.create(user=user)

    info = AttrDict({
        'context': AttrDict({
            'user': user
        }),
        'field_asts': [{}],
        'fragments': {},

    })
    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'team': team_1.id},
        queryset=issues,
        request=AttrDict({
            'user': user
        }),
    ).qs

    assert results.count() == 0


def test_issues_filter_by_team_leader(user):
    user_1 = UserFactory.create()

    team_1 = TeamFactory.create()

    team_1.members.set([user_1, user])

    TeamMember.objects.filter(
        user=user_1, team=team_1
    ).update(
        roles=TeamMember.roles.leader
    )
    TeamMember.objects.filter(
        user=user, team=team_1
    ).update(
        roles=TeamMember.roles.watcher
    )

    issue_1 = IssueFactory.create(user=user_1)
    IssueFactory.create(user=user)

    info = AttrDict({
        'context': AttrDict({
            'user': user
        }),
        'field_asts': [{}],
        'fragments': {},

    })
    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results_filtered = IssuesFilterSet(
        data={'team': team_1.id},
        queryset=issues,
        request=AttrDict({
            'user': user
        }),
    ).qs

    results_ids = [x.id for x in [issue_1]]
    results_ids.sort()

    response_ids = [x.id for x in results_filtered]
    response_ids.sort()

    assert results_ids == response_ids
