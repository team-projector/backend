import pytest

from apps.development.graphql.fields.project_groups import (
    ProjectGroupsConnectionField,
)
from apps.development.models import ProjectGroup
from apps.development.models.choices.project_state import ProjectState
from tests.helpers import lists
from tests.test_development.factories import ProjectGroupFactory


@pytest.fixture()
def groups(db):
    """Generate project groups."""
    return (
        ProjectGroupFactory.create(
            title="C",
            state=ProjectState.DEVELOPING,
            full_title="D",
        ),
        ProjectGroupFactory.create(
            title="B",
            state=ProjectState.ARCHIVED,
            full_title="B",
        ),
        ProjectGroupFactory.create(
            title="A",
            state=ProjectState.SUPPORTING,
            full_title="A",
        ),
    )


@pytest.fixture()
def sort_filter():
    """Returns sorter."""
    return ProjectGroupsConnectionField.sort_handler


@pytest.mark.parametrize(
    ("order_by", "indexes"),
    [
        ("title", (2, 1, 0)),
        ("-title", (0, 1, 2)),
        ("state", (1, 0, 2)),
        ("-state", (2, 0, 1)),
        ("full_title", (2, 1, 0)),
        ("-full_title", (0, 1, 2)),
    ],
)
def test_order_by(groups, order_by, indexes, sort_filter):
    """Test order by."""
    queryset = sort_filter.filter(
        ProjectGroup.objects.all(),
        [order_by],
    )

    assert list(queryset) == lists.sub_list(groups, indexes)
