import pytest

from apps.development.graphql.fields.project_groups import (
    ProjectGroupsFilterSet,
)
from apps.development.models import ProjectGroup
from tests.test_development.factories import ProjectGroupFactory


@pytest.fixture()
def search_filter():
    """Returns sorter."""
    return ProjectGroupsFilterSet.declared_filters["q"]


@pytest.fixture()
def groups(db):
    """Generate projects."""
    return (
        ProjectGroupFactory.create(title="A", gl_url="http://gl.com/a"),
        ProjectGroupFactory.create(title="B", gl_url="http://gl.com/b"),
        ProjectGroupFactory.create(title="C", gl_url="http://gl.com/c"),
    )


def test_search_empty(groups, search_filter):
    """Test empty search."""
    queryset = search_filter.filter(ProjectGroup.objects.all(), "")

    assert queryset.count() == 3


def test_search_not_found(groups, search_filter):
    """Test search not found."""
    queryset = search_filter.filter(ProjectGroup.objects.all(), "d")

    assert not queryset.exists()


def test_search_by_title(groups, search_filter):
    """Test search by title."""
    queryset = search_filter.filter(ProjectGroup.objects.all(), "b")

    assert queryset.count() == 1
    assert queryset.first() == groups[1]


def test_search_by_gl_url(groups, search_filter):
    """Test search by gl_url."""
    queryset = search_filter.filter(
        ProjectGroup.objects.all(),
        groups[2].gl_url,
    )

    assert queryset.count() == 1
    assert queryset.first() == groups[2]


def test_search_by_gl_url_not_found(groups, search_filter):
    """Test search by gl_url not found."""
    queryset = search_filter.filter(
        ProjectGroup.objects.all(),
        "http://gl.com/d",
    )

    assert not queryset.exists()
