from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.models.milestone import Milestone, MilestoneState
from tests.test_development.factories import ProjectMilestoneFactory


def test_filter_by_state(db):
    ProjectMilestoneFactory.create(state=MilestoneState.ACTIVE)
    ProjectMilestoneFactory.create(state=MilestoneState.ACTIVE)
    ProjectMilestoneFactory.create(state=MilestoneState.CLOSED)

    assert MilestonesFilterSet(
        data={"state": MilestoneState.ACTIVE},
        queryset=Milestone.objects.all(),
    ).qs.count() == 2

    assert MilestonesFilterSet(
        data={"state": MilestoneState.CLOSED},
        queryset=Milestone.objects.all(),
    ).qs.count() == 1
