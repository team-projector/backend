import pytest

from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.models import Milestone
from tests.test_development.factories import (
    ProjectFactory,
    ProjectMilestoneFactory,
)


@pytest.fixture()
def project(db):
    """Create project."""
    return ProjectFactory.create()


@pytest.fixture()
def milestones(db):
    """Create project milestones."""
    return ProjectMilestoneFactory.create_batch(4)


def test_empty_filter(milestones):
    """Test not filter."""
    filter_set = MilestonesFilterSet(
        {"project": None},
        queryset=Milestone.objects,
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 4


def test_filter_by_project_empty(project, milestones):
    """Test filter by project."""
    filter_set = MilestonesFilterSet(
        {"project": project.pk},
        queryset=Milestone.objects,
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()


def test_filter_by_project(project, milestones):
    """Test filter by project."""
    project.milestones.add(milestones[2])

    filter_set = MilestonesFilterSet(
        {"project": project.pk},
        queryset=Milestone.objects,
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == milestones[2]
