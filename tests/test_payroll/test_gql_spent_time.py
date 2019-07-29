from datetime import timedelta, date
from django.utils import timezone

from apps.development.models import TeamMember
from apps.payroll.models.spent_time import SpentTime
from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.graphql.types.spent_time import SpentTimeType
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_development.factories_gitlab import AttrDict
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory
from tests.test_users.factories import UserFactory


def test_list(user, client):
    issue = IssueFactory.create()

    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds()))

    spend_2 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=2),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds()))

    spend_3 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=4).total_seconds()))

    spend_4 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds()))

    client.user = user
    info = AttrDict({'context': client})

    spends = SpentTimeType().get_queryset(SpentTime.objects.all(), info)

    results = SpentTimeFilterSet(
        data={'user': user.id},
        queryset=spends,
        request=client,
    ).qs

    assert results.count() == 4
    assert set(results) == {spend_1, spend_2, spend_3, spend_4}


def test_permissions_another_user_but_team_lead(user, client):
    user_2 = UserFactory.create(login='user_2@mail.com')
    spend_user_2 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user_2,
        base=IssueFactory.create(),
        time_spent=int(timedelta(hours=5).total_seconds())
    )

    team = TeamFactory.create()

    TeamMemberFactory.create(
        team=team,
        user=user,
        roles=TeamMember.roles.developer | TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        team=team,
        user=user_2,
        roles=TeamMember.roles.developer
    )

    client.user = user
    info = AttrDict({'context': client})

    spends = SpentTimeType().get_queryset(SpentTime.objects.all(), info)

    results = SpentTimeFilterSet(
        data={'user': user_2.id},
        queryset=spends,
        request=client,
    ).qs

    assert results.count() == 1
    assert results[0] == spend_user_2


def test_permissions_another_user_but_another_team_lead(user, client):
    user_2 = UserFactory.create(login='user_2@mail.com')

    TeamMemberFactory.create(team=TeamFactory.create(),
                             user=user,
                             roles=TeamMember.roles.developer | TeamMember.roles.leader)

    TeamMemberFactory.create(team=TeamFactory.create(),
                             user=user_2,
                             roles=TeamMember.roles.developer)
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user_2,
        base=IssueFactory.create(),
        time_spent=int(timedelta(hours=5).total_seconds())
    )

    client.user = user
    info = AttrDict({'context': client})

    spends = SpentTimeType().get_queryset(SpentTime.objects.all(), info)

    results = SpentTimeFilterSet(
        data={'user': user_2.id},
        queryset=spends,
        request=client,
    ).qs

    assert results.count() == 0


def test_permissions_another_user_but_team_developer(user, client):
    user_2 = UserFactory.create(login='user_2@mail.com')
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user_2,
        base=IssueFactory.create(),
        time_spent=int(timedelta(hours=5).total_seconds())
    )

    client.user = user
    info = AttrDict({'context': client})

    spends = SpentTimeType().get_queryset(SpentTime.objects.all(), info)

    results = SpentTimeFilterSet(
        data={'user': user_2.id},
        queryset=spends,
        request=client,
    ).qs

    assert results.count() == 0


def test_time_expenses_filter_by_team(user, client):
    user_2 = UserFactory.create()
    issue = IssueFactory.create()
    team_member = TeamMemberFactory.create(
        user=user,
        roles=TeamMember.roles.leader,
        team=TeamFactory.create()
    )

    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds())
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
        time_spent=int(timedelta(hours=4).total_seconds())
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds())
    )

    client.user = user
    info = AttrDict({'context': client})

    spends = SpentTimeType().get_queryset(SpentTime.objects.all(), info)

    results = SpentTimeFilterSet(
        data={'team': team_member.team_id},
        queryset=spends,
        request=client,
    ).qs

    assert results.count() == 2
    assert set(results) == {spend_1, spend_3}


def test_time_expenses_filter_by_salary(user, client):
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

    client.user = user
    info = AttrDict({'context': client})

    spends = SpentTimeType().get_queryset(SpentTime.objects.all(), info)

    results = SpentTimeFilterSet(
        data={'salary': salary.id},
        queryset=spends,
        request=client,
    ).qs

    assert results.count() == 2
    assert set(results) == {spend_1, spend_3}


def test_time_expenses_filter_by_date(user, client):
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

    spend_3 = IssueSpentTimeFactory.create(
        date=spend_date,
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

    client.user = user
    info = AttrDict({'context': client})

    spends = SpentTimeType().get_queryset(SpentTime.objects.all(), info)

    results = SpentTimeFilterSet(
        data={'date': '2019-03-03'},
        queryset=spends,
        request=client,
    ).qs

    assert results.count() == 2
    assert set(results) == {spend_1, spend_3}


def test_time_expenses_filter_by_date_and_user(user, client):
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

    client.user = user
    info = AttrDict({'context': client})

    spends = SpentTimeType().get_queryset(SpentTime.objects.all(), info)

    results = SpentTimeFilterSet(
        data={'date': '2019-03-03',
              'user': user.id},
        queryset=spends,
        request=client,
    ).qs

    assert results.count() == 1
    assert results[0] == spend_1


def test_time_expenses_order_by_date(user, client):
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

    client.user = user
    info = AttrDict({'context': client})

    spends = SpentTimeType().get_queryset(SpentTime.objects.all(), info)

    results = SpentTimeFilterSet(
        data={'order_by': 'date'},
        queryset=spends,
        request=client,
    ).qs

    assert list(results) == [spend_1, spend_3, spend_2, spend_4]

    results = SpentTimeFilterSet(
        data={'order_by': '-date'},
        queryset=spends,
        request=client,
    ).qs

    assert list(results) == [spend_4, spend_2, spend_3, spend_1]


def test_double_spent_time(user, client):
    spends = IssueSpentTimeFactory.create_batch(size=10, user=user)

    TeamMemberFactory.create(
        team=TeamFactory.create(),
        user=user,
        roles=TeamMember.roles.leader | TeamMember.roles.watcher
    )
    TeamMemberFactory.create(
        team=TeamFactory.create(),
        user=user,
        roles=TeamMember.roles.leader | TeamMember.roles.watcher
    )

    client.user = user
    info = AttrDict({'context': client})

    queryset = SpentTimeType().get_queryset(SpentTime.objects.all(), info)

    results = SpentTimeFilterSet(
        data={'user': user.id},
        queryset=queryset,
        request=client,
    ).qs

    assert set(results) == set(spends)
