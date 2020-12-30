from jnt_django_toolbox.helpers.time import seconds

from apps.payroll.graphql.fields.all_spent_times import SpentTimeFilterSet
from apps.payroll.models import SpentTime
from tests.test_development.factories import (
    IssueFactory,
    MergeRequestFactory,
    ProjectFactory,
)
from tests.test_payroll.factories import (
    IssueSpentTimeFactory,
    MergeRequestSpentTimeFactory,
)


def test_filter_by_project(user):
    """
    Test filter by project.

    :param user:
    """
    projects = ProjectFactory.create_batch(2)
    issue = IssueFactory.create(user=user, project=projects[0])
    merge_request = MergeRequestFactory.create(user=user, project=projects[1])

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
            user=user,
            base=merge_request,
            time_spent=int(seconds(hours=4)),
        ),
        MergeRequestSpentTimeFactory.create(
            user=user,
            base=merge_request,
            time_spent=int(seconds(hours=1)),
        ),
    ]

    queryset = SpentTimeFilterSet(
        data={"project": projects[0].pk},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(queryset) == set(spends[:2])

    queryset = SpentTimeFilterSet(
        data={"project": projects[1].pk},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(queryset) == set(spends[2:])
