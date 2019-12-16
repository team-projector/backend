from datetime import timedelta

from django.utils import timezone

from apps.core.utils.time import seconds
from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.graphql.types.spent_time import SpentTimeType
from apps.payroll.models.spent_time import SpentTime
from tests.helpers.objects import AttrDict
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_list(user, client):
    issue = IssueFactory.create()

    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user,
        base=issue,
        time_spent=int(seconds(hours=5))
    )
    spend_2 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=2),
        user=user,
        base=issue,
        time_spent=int(seconds(hours=2))
    )
    spend_3 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(seconds(hours=4))
    )
    spend_4 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user,
        base=issue,
        time_spent=int(seconds(minutes=10))
    )

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


def test_owner(user):
    issue = IssueFactory.create()
    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now(),
        user=user,
        base=issue,
        time_spent=0
    )

    merge_request = MergeRequestFactory.create()
    spend_2 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user,
        base=merge_request,
        time_spent=0
    )

    assert SpentTimeType.resolve_owner(spend_1, None) == issue
    assert SpentTimeType.resolve_owner(spend_2, None) == merge_request
