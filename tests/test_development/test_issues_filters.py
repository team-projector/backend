from datetime import timedelta, datetime

from django.core.exceptions import PermissionDenied
from pytest import raises

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.models import TeamMember
from apps.development.models.issue import Issue, ISSUE_STATES
from tests.test_development.factories import (
    IssueFactory,
    TicketFactory,
    ProjectFactory,
    ProjectMilestoneFactory,
    TeamFactory,
    TeamMemberFactory
)
from tests.test_users.factories import UserFactory


def test_filter_by_state(user):
    issue_opened = IssueFactory.create(user=user, state=ISSUE_STATES.OPENED)
    issue_closed = IssueFactory.create(user=user, state=ISSUE_STATES.CLOSED)
    IssueFactory.create_batch(5, user=user, state='')

    results = IssuesFilterSet(
        data={'state': ISSUE_STATES.OPENED},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == issue_opened

    results = IssuesFilterSet(
        data={'state': ISSUE_STATES.CLOSED},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == issue_closed


def test_filter_by_due_date(user):
    issue = IssueFactory.create(user=user, due_date=datetime.now())
    IssueFactory.create(user=user, due_date=datetime.now() + timedelta(days=1))
    IssueFactory.create(user=user, due_date=datetime.now() - timedelta(days=1))

    results = IssuesFilterSet(
        data={'due_date': datetime.now().date()},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == issue


def test_filter_by_due_date_and_state(user):
    issue = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.OPENED,
        due_date=datetime.now()
    )
    IssueFactory.create(
        user=user,
        state=ISSUE_STATES.CLOSED,
        due_date=datetime.now()
    )
    IssueFactory.create(
        user=user,
        state=ISSUE_STATES.CLOSED,
        due_date=datetime.now() - timedelta(days=1)
    )
    IssueFactory.create(
        user=user,
        state=ISSUE_STATES.OPENED,
        due_date=datetime.now() - timedelta(days=1)
    )

    results = IssuesFilterSet(
        data={
            'due_date': datetime.now().date(),
            'state': ISSUE_STATES.OPENED
        },
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == issue


def test_filter_by_project(user):
    project_1 = ProjectFactory.create()
    IssueFactory.create(user=user, project=project_1)

    project_2 = ProjectFactory.create()
    IssueFactory.create(user=user, project=project_2)
    IssueFactory.create_batch(3, user=user)

    results = IssuesFilterSet(
        data={'project': project_1.id},
        queryset=Issue.objects.all(),

    ).qs

    assert results.count() == 1
    assert results.first().project == project_1

    results = IssuesFilterSet(
        data={'project': project_2.id},
        queryset=Issue.objects.all(),

    ).qs

    assert results.count() == 1
    assert results.first().project == project_2


def test_filter_by_team_with_one_member(user):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER
    )

    IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(5, user=UserFactory.create())

    results = IssuesFilterSet(
        data={'team': team.id},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 2
    assert all(issue.user == user for issue in results) is True


def test_filter_by_team_with_many_members(user):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER
    )
    IssueFactory.create_batch(2, user=user)

    another_user = UserFactory.create()
    IssueFactory.create_batch(3, user=another_user)

    TeamMemberFactory.create(
        user=another_user,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )

    IssueFactory.create_batch(4, user=UserFactory.create())

    results = IssuesFilterSet(
        data={'team': team.id},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 5
    assert all(issue.user == user or issue.user == another_user for issue in
               results) is True


def test_filter_by_team_with_watcher(user):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER
    )
    IssueFactory.create_batch(2, user=user)

    another_user = UserFactory.create()
    IssueFactory.create_batch(3, user=another_user)

    another_team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=another_team,
        roles=TeamMember.roles.WATCHER
    )

    TeamMemberFactory.create(
        user=another_user,
        team=another_team,
        roles=TeamMember.roles.DEVELOPER
    )

    results = IssuesFilterSet(
        data={'team': team.id},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 2
    assert all(issue.user == user for issue in results) is True

    results = IssuesFilterSet(
        data={'team': another_team.id},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 3
    assert all(issue.user == another_user for issue in results) is True


def test_filter_by_problems(user):
    issue_problems = IssueFactory.create_batch(2, user=user)
    IssueFactory.create_batch(
        5,
        user=user,
        due_date=datetime.now().date(),
        time_estimate=1000
    )

    results = IssuesFilterSet(
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 7

    results = IssuesFilterSet(
        data={'problems': True},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 2
    assert set(results) == set(issue_problems)

    results = IssuesFilterSet(
        data={'problems': False},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 5
    assert any(issue in issue_problems for issue in results) is False


def test_search(user):
    issue_1 = IssueFactory.create(title='create', user=user, gl_url='foobar')
    issue_2 = IssueFactory.create(title='react', user=user)
    IssueFactory.create(title='test0', user=user)

    results = IssuesFilterSet(
        data={'q': 'ate'},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == issue_1

    results = IssuesFilterSet(
        data={'q': 'rea'},
        queryset=Issue.objects.all(),
    ).qs

    assert results.count() == 2
    assert set(results) == {issue_1, issue_2}

    results = IssuesFilterSet(
        data={'q': '012345'},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 0

    results = IssuesFilterSet(
        data={'q': 'foobar'},
        queryset=Issue.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == issue_1


def test_order_by_title(user):
    issue_1 = IssueFactory.create(title='agent', user=user)
    issue_2 = IssueFactory.create(title='cloud', user=user)
    issue_3 = IssueFactory.create(title='bar', user=user)

    results = IssuesFilterSet(
        data={'order_by': 'title'},
        queryset=Issue.objects.all()
    ).qs

    assert list(results) == [issue_1, issue_3, issue_2]

    results = IssuesFilterSet(
        data={'order_by': '-title'},
        queryset=Issue.objects.all()
    ).qs

    assert list(results) == [issue_2, issue_3, issue_1]


def test_order_by_due_date(user):
    issue_1 = IssueFactory.create(due_date=datetime.now() - timedelta(days=3),
                                  user=user)
    issue_2 = IssueFactory.create(due_date=datetime.now() + timedelta(days=1),
                                  user=user)
    issue_3 = IssueFactory.create(due_date=datetime.now(), user=user)

    results = IssuesFilterSet(
        data={'order_by': 'dueDate'},
        queryset=Issue.objects.all()
    ).qs

    assert list(results) == [issue_1, issue_3, issue_2]

    results = IssuesFilterSet(
        data={'order_by': '-dueDate'},
        queryset=Issue.objects.all()
    ).qs

    assert list(results) == [issue_2, issue_3, issue_1]


def test_filter_by_milestone(user, client):
    user.roles.PROJECT_MANAGER = True
    user.save()

    milestone_1 = ProjectMilestoneFactory.create()
    IssueFactory.create_batch(3, user=user, milestone=milestone_1)

    milestone_2 = ProjectMilestoneFactory.create()
    IssueFactory.create_batch(2, user=user, milestone=milestone_2)

    client.user = user

    results = IssuesFilterSet(
        data={'milestone': milestone_1.id},
        queryset=Issue.objects.all(),
        request=client
    ).qs

    assert results.count() == 3
    assert all([item.milestone == milestone_1 for item in results]) is True

    results = IssuesFilterSet(
        data={'milestone': milestone_2.id},
        queryset=Issue.objects.all(),
        request=client
    ).qs

    assert results.count() == 2
    assert all([item.milestone == milestone_2 for item in results]) is True


def test_filter_by_milestone_not_pm(user, client):
    milestone_1 = ProjectMilestoneFactory.create()
    IssueFactory.create_batch(3, user=user, milestone=milestone_1)

    client.user = user

    with raises(PermissionDenied):
        IssuesFilterSet(
            data={'milestone': milestone_1.id},
            queryset=Issue.objects.all(),
            request=client
        ).qs


def test_filter_by_ticket(user, client):
    user.roles.PROJECT_MANAGER = True
    user.save()

    ticket_1 = TicketFactory.create()
    IssueFactory.create_batch(3, user=user, ticket=ticket_1)

    ticket_2 = TicketFactory.create()
    IssueFactory.create_batch(2, user=user, ticket=ticket_2)

    client.user = user

    results = IssuesFilterSet(
        data={'ticket': ticket_1.id},
        queryset=Issue.objects.all(),
        request=client
    ).qs

    assert results.count() == 3
    assert all([item.ticket == ticket_1 for item in results]) is True

    results = IssuesFilterSet(
        data={'ticket': ticket_2.id},
        queryset=Issue.objects.all(),
        request=client
    ).qs

    assert results.count() == 2
    assert all([item.ticket == ticket_2 for item in results]) is True


def test_filter_by_ticket_not_pm(user, client):
    ticket_1 = TicketFactory.create()
    IssueFactory.create_batch(3, user=user, ticket=ticket_1)

    client.user = user

    with raises(PermissionDenied):
        IssuesFilterSet(
            data={'ticket': ticket_1.id},
            queryset=Issue.objects.all(),
            request=client
        ).qs
