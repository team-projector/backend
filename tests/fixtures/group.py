# -*- coding: utf-8 -*-

import pytest

from apps.development.models.project_member import ProjectMemberRole
from tests.test_development.factories import (
    ProjectGroupFactory,
    ProjectMemberFactory,
)
from tests.test_users.factories import UserFactory


@pytest.fixture()
def group(db):
    """Create test project group."""
    return ProjectGroupFactory.create()


@pytest.fixture()
def make_group_manager():
    """Group manager maker."""
    return _make_group_manager


@pytest.fixture()
def group_manager(group, make_group_manager):
    """Create group manager user."""
    return make_group_manager(group)


@pytest.fixture()
def make_group_developer():
    """Group developer maker."""
    return _make_group_developer


@pytest.fixture()
def group_developer(group, make_group_developer):
    """Create group developer user."""
    return make_group_developer(group)


@pytest.fixture()
def make_group_customer():
    """Group customer maker."""
    return _make_group_customer


@pytest.fixture()
def group_customer(group, make_group_customer):
    """Create project customer user."""
    return make_group_customer(group)


def _make_group_manager(group, user=None):
    """Create or bind group manager."""
    return _add_or_update_user_in_group(
        group, ProjectMemberRole.MANAGER, user,
    )


def _make_group_developer(group, user=None):
    """Create or bind group developer."""
    return _add_or_update_user_in_group(
        group, ProjectMemberRole.DEVELOPER, user,
    )


def _make_group_customer(group, user=None):
    """Create or bind group customer."""
    return _add_or_update_user_in_group(
        group, ProjectMemberRole.CUSTOMER, user,
    )


def _add_or_update_user_in_group(group, role, user):
    """Create user and add into group with given role."""
    if not user:
        user = UserFactory.create()

    ProjectMemberFactory.create(user=user, role=role, owner=group)

    return user
