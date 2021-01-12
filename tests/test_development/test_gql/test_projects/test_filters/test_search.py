import pytest

from apps.development.graphql.fields.projects import ProjectsFilterSet
from apps.development.models import Project
from tests.test_development.factories import ProjectFactory


@pytest.fixture()
def search_filter():
    """Returns sorter."""
    return ProjectsFilterSet.declared_filters["q"]


@pytest.fixture()
def projects(db):
    """Generate projects."""
    return (
        ProjectFactory.create(title="A", gl_url="http://gl.com/a"),
        ProjectFactory.create(title="B", gl_url="http://gl.com/b"),
        ProjectFactory.create(title="C", gl_url="http://gl.com/c"),
    )


def test_search_empty(projects, search_filter):
    """Test empty search."""
    queryset = search_filter.filter(Project.objects.all(), "")

    assert queryset.count() == 3


def test_search_not_found(projects, search_filter):
    """Test search not found."""
    queryset = search_filter.filter(Project.objects.all(), "d")

    assert not queryset.exists()


def test_search_by_title(projects, search_filter):
    """Test search by title."""
    queryset = search_filter.filter(Project.objects.all(), "b")

    assert queryset.count() == 1
    assert queryset.first() == projects[1]


def test_search_by_gl_url(projects, search_filter):
    """Test search by gl_url."""
    queryset = search_filter.filter(
        Project.objects.all(),
        projects[2].gl_url,
    )

    assert queryset.count() == 1
    assert queryset.first() == projects[2]


def test_search_by_gl_url_not_found(projects, search_filter):
    """Test search by gl_url not found."""
    queryset = search_filter.filter(
        Project.objects.all(),
        "http://gl.com/d",
    )

    assert not queryset.exists()
