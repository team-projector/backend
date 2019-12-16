from datetime import datetime, timedelta

from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.models import Milestone
from apps.development.models.milestone import MILESTONE_STATES
from tests.test_development.factories.project_milestone import (
    ProjectMilestoneFactory,
)


def test_filter_by_state(db):
    milestone_active = ProjectMilestoneFactory.create(
        state=MILESTONE_STATES.ACTIVE
    )
    milestone_closed = ProjectMilestoneFactory.create(
        state=MILESTONE_STATES.CLOSED
    )

    results = MilestonesFilterSet(
        data={'active': True},
        queryset=Milestone.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == milestone_active

    results = MilestonesFilterSet(
        data={'active': False},
        queryset=Milestone.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == milestone_closed


def test_order_by_due_date(db):
    milestone_1 = ProjectMilestoneFactory.create(
        due_date=datetime.now() - timedelta(days=3)
    )
    milestone_2 = ProjectMilestoneFactory.create(
        due_date=datetime.now() + timedelta(days=1)
    )
    milestone_3 = ProjectMilestoneFactory.create(
        due_date=datetime.now()
    )

    results = MilestonesFilterSet(
        data={'order_by': 'dueDate'},
        queryset=Milestone.objects.all()
    ).qs

    assert list(results) == [milestone_1, milestone_3, milestone_2]

    results = MilestonesFilterSet(
        data={'order_by': '-dueDate'},
        queryset=Milestone.objects.all()
    ).qs

    assert list(results) == [milestone_2, milestone_3, milestone_1]
