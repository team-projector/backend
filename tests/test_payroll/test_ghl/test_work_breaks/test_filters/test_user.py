# -*- coding: utf-8 -*-

from apps.payroll.graphql.filters import WorkBreakFilterSet
from apps.payroll.models import WorkBreak
from tests.test_payroll.factories import WorkBreakFactory


def test_filter_by_user(team_leader, team_developer):
    """
    Test filter by user.

    :param team_leader:
    :param team_developer:
    """
    work_breaks = [
        WorkBreakFactory.create(user=team_leader),
        WorkBreakFactory.create(user=team_developer),
    ]

    queryset = WorkBreakFilterSet(
        data={"user": team_leader.pk}, queryset=WorkBreak.objects.all(),
    ).qs

    assert queryset.count() == 1
    assert queryset.first() == work_breaks[0]

    queryset = WorkBreakFilterSet(
        data={"user": team_developer.pk}, queryset=WorkBreak.objects.all(),
    ).qs

    assert queryset.count() == 1
    assert queryset.first() == work_breaks[1]
