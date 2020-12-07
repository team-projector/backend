import pytest

from tests.test_development.factories import ProjectFactory


@pytest.fixture()
def project(db):
    """Create test project."""
    return ProjectFactory.create()


@pytest.fixture()
def project_manager(project, make_project_manager):
    """Create project manager user."""
    return make_project_manager(project)


@pytest.fixture()
def project_developer(project, make_project_developer):
    """Create project developer user."""
    return make_project_developer(project)


@pytest.fixture()
def project_customer(project, make_project_customer):
    """Create project customer user."""
    return make_project_customer(project)
