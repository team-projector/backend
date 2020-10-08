import pytest

from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectGroupFactory,
)
from tests.test_development.test_services.test_issues.test_allowed import (
    helpers,
)


@pytest.fixture()
def project(group):
    """Create test project."""
    return ProjectFactory.create(group=group)


def test_manager(project, group_manager, make_group_manager):
    """
    Test manager.

    :param project:
    :param group_manager:
    :param make_group_manager:
    """
    group2 = ProjectGroupFactory.create()
    make_group_manager(group2, group_manager)
    project2 = ProjectFactory.create(group=group2)

    project3 = ProjectFactory.create(group=ProjectGroupFactory.create())
    IssueFactory.create_batch(5, project=project3)

    helpers.check_allowed_for_user(
        group_manager,
        [
            *IssueFactory.create_batch(2, project=project),
            IssueFactory.create(project=project2),
        ],
    )


def test_developer(project, group_developer):
    """
    Test developer.

    :param project:
    :param group_developer:
    """
    IssueFactory.create_batch(5, project=project)
    helpers.check_allowed_for_user(group_developer, [])


def test_customer(project, group_customer):
    """
    Test customer.

    :param project:
    :param group_customer:
    """
    IssueFactory.create_batch(5, project=project)
    helpers.check_allowed_for_user(group_customer, [])


def test_hierarchy(project, group, group_manager):
    """
    Test hierarchy.

    :param project:
    :param group:
    :param group_manager:
    """
    groups = [
        ProjectGroupFactory.create(parent=group),
        ProjectGroupFactory.create(),
    ]

    projects = [
        ProjectFactory.create(group=groups[0]),
        ProjectFactory.create(group=groups[1]),
    ]

    IssueFactory.create_batch(5, project=projects[1])

    helpers.check_allowed_for_user(
        group_manager,
        [
            *IssueFactory.create_batch(2, project=project),
            IssueFactory.create(project=projects[0]),
        ],
    )
