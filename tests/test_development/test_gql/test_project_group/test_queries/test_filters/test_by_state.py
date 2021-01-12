import pytest

from apps.development.graphql.fields.project_groups import (
    ProjectGroupsFilterSet,
)
from apps.development.models import ProjectGroup
from apps.development.models.choices.project_state import ProjectState
from tests.test_development.factories import ProjectGroupFactory


@pytest.fixture()
def groups(db):
    """Generate project groups."""
    return (
        ProjectGroupFactory.create(title="C", state=ProjectState.DEVELOPING),
        ProjectGroupFactory.create(title="B", state=ProjectState.ARCHIVED),
        ProjectGroupFactory.create(title="A", state=ProjectState.SUPPORTING),
    )


@pytest.fixture()
def state_filter():
    """Returns state filter."""
    return ProjectGroupsFilterSet.declared_filters["state"]


def test_filter_empty(groups, state_filter):
    """Test filter empty."""
    queryset = state_filter.filter(
        ProjectGroup.objects.all(),
        [],
    )

    assert queryset.count() == 3


def test_archived(groups, state_filter):
    """Test search by one parameter."""
    queryset = state_filter.filter(
        ProjectGroup.objects.all(),
        [ProjectState.ARCHIVED],
    )

    assert queryset.count() == 1
    assert queryset.first() == groups[1]


def test_archived_developing(groups, state_filter):
    """Test search by two parameters."""
    queryset = state_filter.filter(
        ProjectGroup.objects.all(),
        [ProjectState.ARCHIVED, ProjectState.DEVELOPING],
    )

    assert queryset.count() == 2
    assert set(queryset) == {groups[0], groups[1]}
