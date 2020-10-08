from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.test_services.test_issues.test_allowed import (
    helpers,
)


def test_manager(project, project_manager):
    """
    Test manager.

    :param project:
    :param project_manager:
    """
    IssueFactory.create_batch(5, project=ProjectFactory.create())

    helpers.check_allowed_for_user(
        project_manager,
        IssueFactory.create_batch(2, project=project),
    )


def test_manager_in_many_projects(
    project,
    project_manager,
    make_project_manager,
):
    """
    Test manager in many projects.

    :param project:
    :param project_manager:
    :param make_project_manager:
    """
    project2 = ProjectFactory.create()
    make_project_manager(project2, project_manager)

    IssueFactory.create_batch(5, project=ProjectFactory.create())

    helpers.check_allowed_for_user(
        project_manager,
        [
            *IssueFactory.create_batch(2, project=project),
            IssueFactory.create(project=project2),
        ],
    )


def test_developer(project, project_developer):
    """
    Test developer.

    :param project:
    :param project_developer:
    """
    IssueFactory.create_batch(2, project=project)
    helpers.check_allowed_for_user(project_developer, [])


def test_customer(project, project_customer):
    """
    Test customer.

    :param project:
    :param project_customer:
    """
    IssueFactory.create_batch(5, project=project)
    helpers.check_allowed_for_user(project_customer, [])
