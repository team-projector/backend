import pytest

from apps.development.graphql.fields.projects import ProjectsFilterSet
from apps.development.models import Project
from tests.test_development.factories import ProjectFactory

KEY_SEARCH = "q"


@pytest.fixture()
def projects(db):
    """Generate projects."""
    return (
        ProjectFactory.create(title="A", gl_url="http://gl.com/a"),
        ProjectFactory.create(title="B", gl_url="http://gl.com/b"),
        ProjectFactory.create(title="C", gl_url="http://gl.com/c"),
    )


def test_search_empty(projects):
    """Test search no parameter."""
    filter_set = ProjectsFilterSet(
        {KEY_SEARCH: ""},
        Project.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 3


def test_search_not_found(projects):
    """Test search not found."""
    filter_set = ProjectsFilterSet(
        {KEY_SEARCH: "d"},
        Project.objects.all(),
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()


def test_search_by_title(projects):
    """Test search by title."""
    filter_set = ProjectsFilterSet(
        {KEY_SEARCH: "b"},
        Project.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == projects[1]


def test_search_by_gl_url(projects):
    """Test search by gl_url."""
    filter_set = ProjectsFilterSet(
        {KEY_SEARCH: projects[2].gl_url},
        Project.objects.all(),
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == projects[2]


def test_search_by_gl_url_not_found(projects):
    """Test search by gl_url not found."""
    filter_set = ProjectsFilterSet(
        {KEY_SEARCH: "http://gl.com/d"},
        Project.objects.all(),
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()
