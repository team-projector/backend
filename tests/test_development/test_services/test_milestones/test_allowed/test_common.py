# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.models import Milestone
from apps.development.services.milestone.allowed import filter_allowed_for_user
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
    ProjectMilestoneFactory,
)


def test_not_project_manager(project_developer, group_customer, group):
    project = ProjectFactory.create()
    ProjectMilestoneFactory.create(owner=project)
    ProjectMilestoneFactory.create(owner=group)

    with pytest.raises(GraphQLPermissionDenied):
        filter_allowed_for_user(Milestone.objects.all(), project_developer)


def test_projects(user, make_project_manager):
    projects = ProjectFactory.create_batch(2)
    make_project_manager(projects[0], user)
    make_project_manager(projects[1], user)

    milestones = {
        *ProjectMilestoneFactory.create_batch(2, owner=projects[0]),
        ProjectMilestoneFactory.create(owner=projects[0]),
    }

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(Milestone.objects.all(), user)

    assert queryset.count() == 3
    assert set(queryset) == milestones


def test_groups(user, make_group_manager):
    groups = ProjectGroupFactory.create_batch(2)
    make_group_manager(groups[0], user)
    make_group_manager(groups[1], user)

    milestones = {
        *ProjectMilestoneFactory.create_batch(2, owner=groups[0]),
        ProjectMilestoneFactory.create(owner=groups[0]),
    }

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(Milestone.objects.all(), user)

    assert queryset.count() == 3
    assert set(queryset) == milestones


def test_group_and_projects(user, make_project_manager, make_group_manager):
    group = ProjectGroupFactory.create()
    project = ProjectFactory.create()

    make_group_manager(group, user)
    make_project_manager(project, user)

    milestones = {
        *ProjectMilestoneFactory.create_batch(2, owner=group),
        ProjectMilestoneFactory.create(owner=project),
    }

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(Milestone.objects.all(), user)

    assert queryset.count() == 3
    assert set(queryset) == milestones


def test_group_with_projects(user, make_project_manager, make_group_manager):
    group = ProjectGroupFactory.create()
    projects = ProjectFactory.create_batch(2, group=group)

    make_group_manager(group, user)

    milestones = {
        *ProjectMilestoneFactory.create_batch(2, owner=group),
        ProjectMilestoneFactory.create(owner=projects[0]),
        ProjectMilestoneFactory.create(owner=projects[1]),
    }

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(Milestone.objects.all(), user)

    assert queryset.count() == 4
    assert set(queryset) == milestones


def test_parent_group_with_groups(
    user, make_project_manager, make_group_manager,
):
    parent_group = ProjectGroupFactory.create()
    make_group_manager(parent_group, user)

    groups = ProjectGroupFactory.create_batch(2, parent=parent_group)

    milestones = {
        ProjectMilestoneFactory.create_batch(2, owner=groups[0]),
        ProjectMilestoneFactory.create(owner=groups[1]),
    }

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(Milestone.objects.all(), user)

    assert queryset.count() == 3
    assert set(queryset) == milestones


def test_parent_group_with_groups_and_projects(
    user, make_project_manager, make_group_manager,
):
    parent_group = ProjectGroupFactory.create()
    make_group_manager(parent_group, user)

    groups = ProjectGroupFactory.create_batch(2, parent=parent_group)

    projects = [
        ProjectFactory.create(group=parent_group),
        ProjectFactory.create(group=groups[0]),
        ProjectFactory.create(group=groups[1]),
    ]

    milestones = {
        ProjectMilestoneFactory.create(owner=groups[0]),
        ProjectMilestoneFactory.create(owner=groups[1]),
        ProjectMilestoneFactory.create(owner=projects[0]),
        ProjectMilestoneFactory.create(owner=projects[1]),
        ProjectMilestoneFactory.create(owner=projects[2]),
    }

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(Milestone.objects.all(), user)

    assert queryset.count() == 5
    assert set(queryset) == milestones
