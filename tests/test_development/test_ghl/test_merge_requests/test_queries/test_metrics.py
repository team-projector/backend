from jnt_django_toolbox.helpers.time import seconds

from apps.development.graphql.types import MergeRequestType
from tests.test_development.factories import MergeRequestFactory


def test_metrics(user):
    """Test merge request metrics type."""
    merge_request = MergeRequestFactory.create(
        user=user,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=2),
    )

    metrics = MergeRequestType.resolve_metrics(merge_request, None)
    assert metrics.remains == seconds(hours=1)
