# -*- coding: utf-8 -*-

from datetime import timedelta

from django.utils import timezone

from apps.payroll.graphql.types.spent_time import SpentTimeType
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_owner(user):
    issue = IssueFactory.create()
    merge_request = MergeRequestFactory.create()

    spends = [
        IssueSpentTimeFactory.create(
            date=timezone.now(), user=user, base=issue, time_spent=0,
        ),
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=4),
            user=user,
            base=merge_request,
            time_spent=0,
        ),
    ]

    assert SpentTimeType.resolve_owner(spends[0], None) == issue
    assert SpentTimeType.resolve_owner(spends[1], None) == merge_request
