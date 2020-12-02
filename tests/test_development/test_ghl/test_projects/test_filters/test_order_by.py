import pytest

from apps.development.graphql.filters import ProjectsFilterSet
from apps.development.models import Project
from apps.development.models.choices.project_state import ProjectState
from tests.helpers import lists
from tests.test_development.factories import ProjectFactory


@pytest.fixture()
def projects(db):
    """Generate projects."""
    return (
        ProjectFactory.create(
            title="C",
            state=ProjectState.DEVELOPING,
            full_title="D",
        ),
        ProjectFactory.create(
            title="B",
            state=ProjectState.ARCHIVED,
            full_title="B",
        ),
        ProjectFactory.create(
            title="A",
            state=ProjectState.SUPPORTING,
            full_title="A",
        ),
    )


@pytest.mark.parametrize(
    ("order_by", "indexes"),
    [
        ("title", (2, 1, 0)),
        ("-title", (0, 1, 2)),
        ("state", (1, 0, 2)),
        ("-state", (2, 0, 1)),
        ("fullTitle", (2, 1, 0)),
        ("-fullTitle", (0, 1, 2)),
    ],
)
def test_order_by(projects, order_by, indexes):
    """Test order by."""
    filter_set = ProjectsFilterSet(
        {"order_by": order_by},
        Project.objects.all(),
    )

    assert filter_set.is_valid()
    assert list(filter_set.qs) == lists.sub_list(projects, indexes)
