from apps.development.models.issue import STATE_OPENED, STATE_CLOSED
from apps.development.services.metrics.feature import get_feature_metrics
from tests.test_development.factories import (
    IssueFactory, FeatureFactory, ProjectGroupMilestoneFactory
)


def test_metrics(db):
    milestone = ProjectGroupMilestoneFactory.create()

    feature = FeatureFactory.create(milestone=milestone)
    IssueFactory.create(
        feature=feature,
        state=STATE_OPENED,
        total_time_spent=0,
        time_estimate=45
    )
    IssueFactory.create(
        feature=feature,
        state=STATE_CLOSED,
        total_time_spent=30,
        time_estimate=60
    )
    IssueFactory.create(
        feature=feature,
        state=STATE_CLOSED,
        total_time_spent=60,
        time_estimate=60
    )

    metrics = get_feature_metrics(feature)

    assert metrics.issues_count == 3
    assert metrics.issues_closed_count == 2
    assert metrics.issues_opened_count == 1
    assert metrics.time_estimate == 165
    assert metrics.time_spent == 90
