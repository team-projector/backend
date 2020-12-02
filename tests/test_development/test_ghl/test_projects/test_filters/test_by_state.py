import pytest

from apps.development.graphql.filters import ProjectsFilterSet
from apps.development.models import Project
from apps.development.models.choices.project_state import ProjectState
from tests.test_development.factories import ProjectFactory


@pytest.fixture()
def projects(db):
    """Generate projects."""
    return (
        ProjectFactory.create(title="C", state=ProjectState.DEVELOPING),
        ProjectFactory.create(title="B", state=ProjectState.ARCHIVED),
        ProjectFactory.create(title="A", state=ProjectState.SUPPORTING),
    )


def test_filter_empty(projects):
    """Test filter empty."""
    filter_set = ProjectsFilterSet(
        {"state": ""},
        Project.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 3


def test_archived(projects):
    """Test search by one parameter."""
    filter_set = ProjectsFilterSet(
        {"state": [ProjectState.ARCHIVED]},
        Project.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == projects[1]


def test_archived_developing(projects):
    """Test search by two parameters."""
    filter_set = ProjectsFilterSet(
        {"state": [ProjectState.ARCHIVED, ProjectState.DEVELOPING]},
        Project.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 2
    assert set(filter_set.qs) == {projects[0], projects[1]}
