# -*- coding: utf-8 -*-

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
    IssueFactory.create_batch(5, project=project)
    helpers.check_allowed_for_user(group_developer, [])


def test_customer(project, group_customer):
    IssueFactory.create_batch(5, project=project)
    helpers.check_allowed_for_user(group_customer, [])


def test_hierarchy(project, group, group_manager):
    sub_group = ProjectGroupFactory.create(parent=group)
    project2 = ProjectFactory.create(group=sub_group)

    group_another = ProjectGroupFactory.create()
    project3 = ProjectFactory.create(group=group_another)
    IssueFactory.create_batch(5, project=project3)

    helpers.check_allowed_for_user(
        group_manager,
        [
            *IssueFactory.create_batch(2, project=project),
            IssueFactory.create(project=project2),
        ],
    )
