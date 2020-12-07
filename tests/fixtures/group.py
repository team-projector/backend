import pytest

from tests.test_development.factories import ProjectGroupFactory


@pytest.fixture()
def group(db):
    """Create test project group."""
    return ProjectGroupFactory.create()


@pytest.fixture()
def group_manager(group, make_group_manager):
    """Create group manager user."""
    return make_group_manager(group)


@pytest.fixture()
def group_developer(group, make_group_developer):
    """Create group developer user."""
    return make_group_developer(group)


@pytest.fixture()
def group_customer(group, make_group_customer):
    """Create project customer user."""
    return make_group_customer(group)
