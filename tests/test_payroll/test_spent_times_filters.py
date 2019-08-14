from datetime import timedelta, date
from django.utils import timezone

from apps.development.models import TeamMember
from apps.payroll.models.spent_time import SpentTime
from apps.payroll.graphql.filters import SpentTimeFilterSet
from tests.test_development.factories import (
    IssueFactory, MergeRequestFactory, ProjectFactory, TeamFactory,
    TeamMemberFactory
)
from tests.test_payroll.factories import (
    IssueSpentTimeFactory, MergeRequestSpentTimeFactory, SalaryFactory
)
from tests.test_users.factories import UserFactory


def test_filter_by_salary(user):
    user_2 = UserFactory.create()
    issue = IssueFactory.create()
    salary = SalaryFactory.create(user=user)

    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds()),
        salary=salary
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=2),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds())
    )

    spend_3 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=4).total_seconds()),
        salary=salary
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds())
    )

    results = SpentTimeFilterSet(
        data={'salary': salary.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert results.count() == 2
    assert set(results) == {spend_1, spend_3}


def test_filter_by_date(user):
    user_2 = UserFactory.create()
    issue = IssueFactory.create()
    spend_date = date(2019, 3, 3)

    spend_1 = IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds()),
        date=spend_date,
    )

    spend_2 = IssueSpentTimeFactory.create(
        user=user_2,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds()),
        date=spend_date
    )

    IssueSpentTimeFactory.create(
        user=user_2,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds()),
        date=timezone.now() - timedelta(hours=1)
    )

    results = SpentTimeFilterSet(
        data={'date': '2019-03-03'},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert results.count() == 2
    assert set(results) == {spend_1, spend_2}


def test_by_date_and_user(user):
    user_2 = UserFactory.create()
    issue = IssueFactory.create()
    spend_date = date(2019, 3, 3)

    spend_1 = IssueSpentTimeFactory.create(
        date=spend_date,
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds()),
    )

    IssueSpentTimeFactory.create(
        user=user_2,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds()),
        date=spend_date
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=4).total_seconds()),
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds())
    )

    results = SpentTimeFilterSet(
        data={'date': '2019-03-03',
              'user': user.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert results.count() == 1
    assert results[0] == spend_1


def test_filter_by_project(user):
    project_1 = ProjectFactory.create()
    issue = IssueFactory.create(user=user, project=project_1)

    spend_1 = IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds())
    )

    spend_2 = IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds())
    )

    project_2 = ProjectFactory.create()
    merge_request = MergeRequestFactory.create(user=user, project=project_2)

    spend_3 = MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        time_spent=int(timedelta(hours=4).total_seconds()),
    )

    spend_4 = MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        time_spent=int(timedelta(hours=1).total_seconds())
    )

    results = SpentTimeFilterSet(
        data={'project': project_1.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(results) == {spend_1, spend_2}

    results = SpentTimeFilterSet(
        data={'project': project_2.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(results) == {spend_3, spend_4}


def test_filter_by_team(user):
    team_1 = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team_1,
        roles=TeamMember.roles.leader
    )

    another_user = UserFactory.create()
    team_2 = TeamFactory.create()
    TeamMemberFactory.create(
        user=another_user,
        team=team_2,
        roles=TeamMember.roles.leader
    )

    issue = IssueFactory.create(user=another_user)

    spend_1 = IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds())
    )

    spend_2 = IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds())
    )

    merge_request = MergeRequestFactory.create(user=user)

    spend_3 = MergeRequestSpentTimeFactory.create(
        user=another_user,
        base=merge_request,
        time_spent=int(timedelta(hours=4).total_seconds()),
    )

    spend_4 = MergeRequestSpentTimeFactory.create(
        user=another_user,
        base=merge_request,
        time_spent=int(timedelta(hours=1).total_seconds())
    )

    results = SpentTimeFilterSet(
        data={'team': team_1.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(results) == {spend_1, spend_2}

    results = SpentTimeFilterSet(
        data={'team': team_2.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(results) == {spend_3, spend_4}


def test_order_by_date(user):
    issue = IssueFactory.create()

    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=4),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds())
    )

    spend_2 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds())
    )

    spend_3 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=3),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=4).total_seconds()),
    )

    spend_4 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1),
        user=user,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds())
    )

    results = SpentTimeFilterSet(
        data={'order_by': 'date'},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert list(results) == [spend_1, spend_3, spend_2, spend_4]

    results = SpentTimeFilterSet(
        data={'order_by': '-date'},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert list(results) == [spend_4, spend_2, spend_3, spend_1]
