import pytest

from apps.development.graphql.fields.projects import ProjectsFilterSet
from apps.development.models import Project
from apps.development.models.choices.project_state import ProjectState
from tests.test_development.factories import ProjectFactory


@pytest.fixture()
def projects(db):
    """Generate project groups."""
    return (
        ProjectFactory.create(title="C", state=ProjectState.DEVELOPING),
        ProjectFactory.create(title="B", state=ProjectState.ARCHIVED),
        ProjectFactory.create(title="A", state=ProjectState.SUPPORTING),
    )


@pytest.fixture()
def state_filter():
    """Returns state filter."""
    return ProjectsFilterSet.declared_filters["state"]


def test_filter_empty(projects, state_filter):
    """Test filter empty."""
    queryset = state_filter.filter(
        Project.objects.all(),
        [],
    )

    assert queryset.count() == 3


def test_archived(projects, state_filter):
    """Test search by one parameter."""
    queryset = state_filter.filter(
        Project.objects.all(),
        [ProjectState.ARCHIVED],
    )

    assert queryset.count() == 1
    assert queryset.first() == projects[1]


def test_archived_developing(projects, state_filter):
    """Test search by two parameters."""
    queryset = state_filter.filter(
        Project.objects.all(),
        [ProjectState.ARCHIVED, ProjectState.DEVELOPING],
    )

    assert queryset.count() == 2
    assert set(queryset) == {projects[0], projects[1]}
