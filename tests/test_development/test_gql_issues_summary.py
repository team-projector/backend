from datetime import datetime, timedelta
from django.utils import timezone

from apps.development.graphql.resolvers import resolve_issues_summary
from apps.development.models import TeamMember
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_development.factories_gitlab import AttrDict
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


def test_one_user(user):
    IssueFactory.create_batch(
        5, user=user,
        total_time_spent=0,
        due_date=datetime.now()
    )

    info = AttrDict({
        'context': AttrDict({
            'user': user
        })
    })

    results = resolve_issues_summary(None, info=info, user=user.id)

    _check_summary(results, 5, 0, 0)


def test_filter_by_user(user):
    IssueFactory.create_batch(5, user=user, total_time_spent=0,
                              due_date=datetime.now())

    another_user = UserFactory.create()
    IssueFactory.create_batch(5, user=another_user, total_time_spent=0,
                              due_date=datetime.now())

    info = AttrDict({
        'context': AttrDict({
            'user': user
        })
    })

    results = resolve_issues_summary(None, info=info, user=user.id)

    _check_summary(results, 5, 0, 0)


def test_time_spents_by_user(user):
    issues = IssueFactory.create_batch(5, user=user,
                                       due_date=datetime.now())

    another_user = UserFactory.create()

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=another_user,
        base=IssueFactory.create(user=another_user),
        time_spent=300
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issues[0],
        time_spent=100
    )

    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=2),
        user=user,
        base=issues[0],
        time_spent=200
    )

    info = AttrDict({
        'context': AttrDict({
            'user': user
        })
    })

    results = resolve_issues_summary(
        None, info=info, user=user.id, due_date=datetime.now().date()
    )

    _check_summary(results, 5, 100, 0)


def test_time_spents_by_team(user):
    issues = IssueFactory.create_batch(5, user=user,
                                       due_date=datetime.now())

    another_user = UserFactory.create()

    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=another_user,
        team=TeamFactory.create(),
        roles=TeamMember.roles.developer
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=another_user,
        base=IssueFactory.create(user=another_user),
        time_spent=300
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issues[0],
        time_spent=100
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2),
        user=user,
        base=issues[0],
        time_spent=200
    )

    info = AttrDict({
        'context': AttrDict({
            'user': user
        })
    })

    results = resolve_issues_summary(
        None, info=info, team=team.id, due_date=timezone.now().date()
    )

    _check_summary(results, 5, 100, 0)


def test_problems(user):
    IssueFactory.create_batch(
        4,
        user=user,
        total_time_spent=0
    )
    IssueFactory.create_batch(
        1,
        user=user,
        total_time_spent=0,
        due_date=datetime.now()
    )

    IssueFactory.create_batch(
        2,
        user=UserFactory.create(),
        total_time_spent=0
    )

    info = AttrDict({
        'context': AttrDict({
            'user': user
        })
    })

    results = resolve_issues_summary(None, info=info, user=user.id)

    _check_summary(results, 5, 0, 4)


def _check_summary(data, issues_count, time_spent, problems_count):
    assert data.issues_count == issues_count
    assert data.time_spent == time_spent
    assert data.problems_count == problems_count
