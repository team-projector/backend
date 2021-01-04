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


def test_filter_empty(groups):
    """Test filter empty."""
    filter_set = ProjectGroupsFilterSet(
        {"state": ""},
        ProjectGroup.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 3


def test_archived(groups):
    """Test search by one parameter."""
    filter_set = ProjectGroupsFilterSet(
        {"state": [ProjectState.ARCHIVED]},
        ProjectGroup.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == groups[1]


def test_archived_developing(groups):
    """Test search by two parameters."""
    filter_set = ProjectGroupsFilterSet(
        {"state": [ProjectState.ARCHIVED, ProjectState.DEVELOPING]},
        ProjectGroup.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 2
    assert set(filter_set.qs) == {groups[0], groups[1]}
