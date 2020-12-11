from apps.development.models import Milestone
from apps.development.models.milestone import MilestoneState
from apps.development.services.milestone.summary import (
    MilestonesSummaryProvider,
)
from tests.test_development.factories import (
    ProjectFactory,
    ProjectMilestoneFactory,
)

KEY_COUNT = "count"
KEY_ACTIVE_COUNT = "active_count"


def test_all_fields(db):
    """
    Test all fields.

    :param db:
    """
    summary = MilestonesSummaryProvider(Milestone.objects.all()).get_data()
    assert summary == {KEY_COUNT: 0, KEY_ACTIVE_COUNT: 0, "closed_count": 0}


def test_selected_fields(db):
    """
    Test selected fields.

    :param db:
    """
    summary = MilestonesSummaryProvider(
        Milestone.objects.all(),
        fields=("count", "active_count"),
    ).get_data()

    assert summary == {KEY_COUNT: 0, KEY_ACTIVE_COUNT: 0}


def test_prefiltered_qs(db):
    """
    Test prefiltered qs.

    :param db:
    """
    project = ProjectFactory.create()
    ProjectMilestoneFactory.create(state=MilestoneState.ACTIVE, owner=project)
    ProjectMilestoneFactory.create(state=MilestoneState.CLOSED, owner=project)
    ProjectMilestoneFactory.create(state=MilestoneState.ACTIVE)
    ProjectMilestoneFactory.create(state=MilestoneState.CLOSED)

    summary = MilestonesSummaryProvider(
        Milestone.objects.filter(object_id=project.id),
        fields=("count", "active_count", "closed_count"),
    ).get_data()

    assert summary == {KEY_COUNT: 2, KEY_ACTIVE_COUNT: 1, "closed_count": 1}
