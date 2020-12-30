from jnt_django_toolbox.helpers.time import seconds

from apps.payroll.graphql.fields.all_spent_times import SpentTimeFilterSet
from apps.payroll.models import SpentTime
from tests.test_development.factories import (
    IssueFactory,
    MergeRequestFactory,
    TeamFactory,
)
from tests.test_payroll.factories import (
    IssueSpentTimeFactory,
    MergeRequestSpentTimeFactory,
)


def test_filter_by_team(user, user2, make_team_leader):
    """
    Test filter by team.

    :param user:
    :param user2:
    :param make_team_leader:
    """
    teams = TeamFactory.create_batch(2)

    make_team_leader(teams[0], user)
    make_team_leader(teams[1], user2)

    issue = IssueFactory.create(user=user2)
    merge_request = MergeRequestFactory.create(user=user)

    spends = [
        IssueSpentTimeFactory.create(
            user=user,
            base=issue,
            time_spent=int(seconds(hours=5)),
        ),
        IssueSpentTimeFactory.create(
            user=user,
            base=issue,
            time_spent=int(seconds(hours=2)),
        ),
        MergeRequestSpentTimeFactory.create(
            user=user2,
            base=merge_request,
            time_spent=int(seconds(hours=4)),
        ),
        MergeRequestSpentTimeFactory.create(
            user=user2,
            base=merge_request,
            time_spent=int(seconds(hours=1)),
        ),
    ]

    queryset = SpentTimeFilterSet(
        data={"team": teams[0].id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(queryset) == set(spends[:2])

    queryset = SpentTimeFilterSet(
        data={"team": teams[1].id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(queryset) == set(spends[2:])
