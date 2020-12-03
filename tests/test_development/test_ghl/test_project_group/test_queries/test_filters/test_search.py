import pytest

from apps.development.graphql.filters import ProjectGroupsFilterSet
from apps.development.models import ProjectGroup
from tests.test_development.factories import ProjectGroupFactory


@pytest.fixture()
def groups(db):
    """Generate projects."""
    return (
        ProjectGroupFactory.create(title="A", gl_url="http://gl.com/a"),
        ProjectGroupFactory.create(title="B", gl_url="http://gl.com/b"),
        ProjectGroupFactory.create(title="C", gl_url="http://gl.com/c"),
    )


def test_search_empty(groups):
    """Test search no parameter."""
    filter_set = ProjectGroupsFilterSet(
        {"q": ""},
        ProjectGroup.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 3


def test_search_not_found(groups):
    """Test search not found."""
    filter_set = ProjectGroupsFilterSet(
        {"q": "d"},
        ProjectGroup.objects.all(),
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()


def test_search_by_title(groups):
    """Test search by title."""
    filter_set = ProjectGroupsFilterSet(
        {"q": "b"},
        ProjectGroup.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == groups[1]


def test_search_by_gl_url(groups):
    """Test search by gl_url."""
    filter_set = ProjectGroupsFilterSet(
        {"q": groups[2].gl_url},
        ProjectGroup.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == groups[2]


def test_search_by_gl_url_not_found(groups):
    """Test search by gl_url not found."""
    filter_set = ProjectGroupsFilterSet(
        {"q": "http://gl.com/d"},
        ProjectGroup.objects.all(),
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()
