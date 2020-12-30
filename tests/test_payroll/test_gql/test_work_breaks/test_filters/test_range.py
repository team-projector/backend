from datetime import timedelta

import pytest
from django.utils import timezone

from apps.payroll.graphql.fields.all_work_breaks import AllWorkBreakFilterSet
from apps.payroll.models import WorkBreak
from tests.test_payroll.factories import WorkBreakFactory


@pytest.mark.parametrize(
    ("from_datetime", "to_datetime"),
    [
        (
            timezone.now() + timedelta(days=1),
            timezone.now() + timedelta(days=3),
        ),
        (
            timezone.now() - timedelta(days=7),
            timezone.now() + timedelta(days=3),
        ),
        (
            timezone.now() + timedelta(days=1),
            timezone.now() + timedelta(days=7),
        ),
        (
            timezone.now() - timedelta(days=7),
            timezone.now() + timedelta(days=7),
        ),
    ],
)
def test_include(team_leader, team_developer, from_datetime, to_datetime):
    """
    Test filter by user.

    :param team_leader:
    :param team_developer:
    """
    work_breaks = [
        WorkBreakFactory.create(
            from_date=from_datetime.date(),
            to_date=to_datetime.date(),
        ),
        WorkBreakFactory.create(
            from_date=(timezone.now() + timedelta(days=10)).date(),
            to_date=(timezone.now() + timedelta(days=15)).date(),
        ),
    ]

    queryset = AllWorkBreakFilterSet(
        data={
            "from_date": (timezone.now() - timedelta(days=5)).date(),
            "to_date": (timezone.now() + timedelta(days=5)).date(),
        },
        queryset=WorkBreak.objects.all(),
    ).qs

    assert queryset.count() == 1
    assert queryset.first() == work_breaks[0]


@pytest.mark.parametrize(
    ("from_datetime", "to_datetime"),
    [
        (
            timezone.now() - timedelta(days=10),
            timezone.now() - timedelta(days=7),
        ),
        (
            timezone.now() + timedelta(days=7),
            timezone.now() + timedelta(days=10),
        ),
    ],
)
def test_exclude(team_leader, team_developer, from_datetime, to_datetime):
    """
    Test filter by user.

    :param team_leader:
    :param team_developer:
    """
    WorkBreakFactory.create(
        from_date=from_datetime.date(),
        to_date=to_datetime.date(),
    )

    queryset = AllWorkBreakFilterSet(
        data={
            "from_date": (timezone.now() - timedelta(days=5)).date(),
            "to_date": (timezone.now() + timedelta(days=5)).date(),
        },
        queryset=WorkBreak.objects.all(),
    ).qs

    assert not queryset.exists()
