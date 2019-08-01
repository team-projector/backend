from datetime import timedelta, datetime

from apps.development.models import TeamMember
from apps.development.graphql.types.issue import IssueType
from apps.development.models.issue import Issue, STATE_CLOSED, STATE_OPENED
from apps.development.graphql.filters import IssuesFilterSet
from tests.base import format_date
from tests.test_development.factories import (
    IssueFactory, ProjectFactory, TeamFactory, TeamMemberFactory
)
from tests.test_development.factories_gitlab import AttrDict
from tests.test_users.factories import UserFactory


def test_issue(user, client):
    issue = IssueFactory.create(user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    node = IssueType().get_node(info, issue.id)

    assert node == issue


def test_all_issues(user, client):
    IssueFactory.create_batch(5, user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    assert issues.count() == 5


def test_show_participants(user, client):
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

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'user': user_2.id},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 1
    assert set(
        x.id for x in results.first().participants.all()
    ) == set(x.id for x in users)


def test_show_users(user, client):
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

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 2
    assert set(x.user.id for x in results) == {user.id, user_2.id}


def test_issues_filter_by_team_empty(user, client):
    user_1 = UserFactory.create()
    user_2 = UserFactory.create()

    team_1 = TeamFactory.create()
    team_2 = TeamFactory.create()

    team_1.members.set([user_1, user_2])
    team_2.members.add(user_2)

    IssueFactory.create(user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'team': team_1.id},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 0


def test_issues_filter_by_team_watcher_empty(user, client):
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

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'team': team_1.id},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 0


def test_issues_filter_by_team_leader(user, client):
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

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results_filtered = IssuesFilterSet(
        data={'team': team_1.id},
        queryset=issues,
        request=client
    ).qs

    results_ids = [x.id for x in [issue_1]]
    results_ids.sort()

    response_ids = [x.id for x in results_filtered]
    response_ids.sort()

    assert results_ids == response_ids


def test_filter_by_state(user, client):
    IssueFactory.create(user=user, state=STATE_OPENED)
    issue = IssueFactory.create(user=user, state=STATE_CLOSED)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'state': STATE_CLOSED},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 1
    assert results[0] == issue


def test_filter_by_due_date(user, client):
    now = datetime.now()
    issue = IssueFactory.create(user=user, state=STATE_OPENED,
                                due_date=now)
    IssueFactory.create(user=user, due_date=now + timedelta(days=1))
    IssueFactory.create(user=user, due_date=now - timedelta(days=1))

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'due_date': format_date(datetime.now())},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 1
    assert results[0] == issue


def test_filter_by_due_date_and_state(user, client):
    now = datetime.now()
    issue = IssueFactory.create(user=user, state=STATE_OPENED,
                                due_date=now)
    IssueFactory.create(user=user, state=STATE_CLOSED,
                        due_date=now + timedelta(days=1))
    IssueFactory.create(user=user, state=STATE_CLOSED,
                        due_date=now - timedelta(days=1))
    IssueFactory.create(user=user, state=STATE_OPENED,
                        due_date=now - timedelta(days=1))

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'due_date': format_date(datetime.now()),
              'state': STATE_OPENED},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 1
    assert results[0] == issue


def test_search(user, client):
    issue_1 = IssueFactory.create(title='create', user=user)
    issue_2 = IssueFactory.create(title='react', user=user)
    IssueFactory.create(title='test0', user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'q': 'ate'},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 1
    assert results.first() == issue_1

    results = IssuesFilterSet(
        data={'q': 'rea'},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 2
    assert set(results) == {issue_1, issue_2}

    results = IssuesFilterSet(
        data={'q': '012345'},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 0


def test_issues_filter_by_project(user, client):
    team = TeamFactory.create()
    team.members.set([user])

    TeamMember.objects.filter(
        user=user, team=team
    ).update(
        roles=TeamMember.roles.leader
    )

    project_1 = ProjectFactory.create()
    IssueFactory.create(user=user, project=project_1)

    project_2 = ProjectFactory.create()
    IssueFactory.create(user=user, project=project_2)
    IssueFactory.create_batch(3, user=user)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    results = IssuesFilterSet(
        data={'project': project_1.id},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 1
    assert results.first().project == project_1

    results = IssuesFilterSet(
        data={'project': project_2.id},
        queryset=issues,
        request=client
    ).qs

    assert results.count() == 1
    assert results.first().project == project_2
