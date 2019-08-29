from apps.core.utils.time import seconds
from apps.development.graphql.types import FeatureType
from apps.development.models.issue import STATE_OPENED, STATE_CLOSED
from apps.development.services.metrics.feature import get_feature_metrics
from tests.test_development.factories import IssueFactory, FeatureFactory


def test_metrics(db):
    feature = FeatureFactory.create()

    IssueFactory.create(
        feature=feature,
        state=STATE_OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1)
    )
    IssueFactory.create(
        feature=feature,
        state=STATE_CLOSED,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=2)
    )
    IssueFactory.create(
        feature=feature,
        state=STATE_CLOSED,
        total_time_spent=seconds(hours=2),
        time_estimate=seconds(hours=2)
    )

    metrics = get_feature_metrics(feature)

    assert metrics.issues_count == 3
    assert metrics.issues_closed_count == 2
    assert metrics.issues_opened_count == 1
    assert metrics.time_estimate == seconds(hours=5)
    assert metrics.time_spent == seconds(hours=3)


def test_resolver(db):
    feature = FeatureFactory.create()

    IssueFactory.create(
        feature=feature,
        state=STATE_OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1)
    )

    metrics = FeatureType.resolve_metrics(feature, None)

    assert metrics.issues_count == 1
    assert metrics.time_estimate == seconds(hours=1)
