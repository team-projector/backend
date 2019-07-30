from datetime import datetime, timedelta
from django.utils import timezone

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.services.allowed.issues import filter_allowed_for_user
from apps.development.services.summary.issues import get_issues_summary
from apps.development.models import Issue, TeamMember
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


def test_one_user(user, client):
    IssueFactory.create_batch(
        5, user=user,
        total_time_spent=0,
        due_date=datetime.now()
    )

    filterset = IssuesFilterSet(
        data={'user': user.id},
        queryset=filter_allowed_for_user(
            Issue.objects.all(),
            user
        ),
        request=client
    )

    results = get_issues_summary(
        filterset.qs,
        filterset.form.cleaned_data['due_date'],
        filterset.form.cleaned_data['user'],
        filterset.form.cleaned_data['team']
    )

    _check_summary(results, 5, 0, 0)


def test_filter_by_user(user, client):
    IssueFactory.create_batch(5, user=user, total_time_spent=0,
                              due_date=datetime.now())

    another_user = UserFactory.create()
    IssueFactory.create_batch(5, user=another_user, total_time_spent=0,
                              due_date=datetime.now())

    filterset = IssuesFilterSet(
        data={'user': user.id},
        queryset=filter_allowed_for_user(
            Issue.objects.all(),
            user
        ),
        request=client
    )

    results = get_issues_summary(
        filterset.qs,
        filterset.form.cleaned_data['due_date'],
        filterset.form.cleaned_data['user'],
        filterset.form.cleaned_data['team']
    )

    _check_summary(results, 5, 0, 0)


def test_time_spents_by_user(user, client):
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

    filterset = IssuesFilterSet(
        data={'user': user.id,
              'due_date': datetime.now().date()},
        queryset=filter_allowed_for_user(
            Issue.objects.all(),
            user
        ),
        request=client
    )

    results = get_issues_summary(
        filterset.qs,
        filterset.form.cleaned_data['due_date'],
        filterset.form.cleaned_data['user'],
        filterset.form.cleaned_data['team']
    )

    _check_summary(results, 5, 100, 0)


def test_time_spents_by_team(user, client):
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

    filterset = IssuesFilterSet(
        data={'team': team.id,
              'due_date': datetime.now().date()},
        queryset=filter_allowed_for_user(
            Issue.objects.all(),
            user
        ),
        request=client
    )

    results = get_issues_summary(
        filterset.qs,
        filterset.form.cleaned_data['due_date'],
        filterset.form.cleaned_data['user'],
        filterset.form.cleaned_data['team']
    )

    _check_summary(results, 5, 100, 0)


def test_problems(user, client):
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

    filterset = IssuesFilterSet(
        data={'user': user.id},
        queryset=filter_allowed_for_user(
            Issue.objects.all(),
            user
        ),
        request=client
    )

    results = get_issues_summary(
        filterset.qs,
        filterset.form.cleaned_data['due_date'],
        filterset.form.cleaned_data['user'],
        filterset.form.cleaned_data['team']
    )

    _check_summary(results, 5, 0, 4)


def _check_summary(data, issues_count, time_spent, problems_count):
    assert data.issues_count == issues_count
    assert data.time_spent == time_spent
    assert data.problems_count == problems_count
