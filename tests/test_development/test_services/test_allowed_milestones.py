from django.core.exceptions import PermissionDenied
from pytest import raises

from apps.development.models import Milestone
from apps.development.models.project_member import PROJECT_MEMBER_ROLES
from apps.development.services.milestone.allowed import filter_allowed_for_user
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
    ProjectMemberFactory,
    ProjectMilestoneFactory,
)


def test_not_pm(user):
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.DEVELOPER,
        owner=project
    )

    ProjectMilestoneFactory.create(owner=project)

    group = ProjectGroupFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.CUSTOMER,
        owner=group
    )

    ProjectMilestoneFactory.create(owner=group)

    with raises(PermissionDenied):
        filter_allowed_for_user(Milestone.objects.all(), user)


def test_projects(user):
    project_1 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=project_1
    )

    milestone_1 = ProjectMilestoneFactory.create(owner=project_1)
    milestone_2 = ProjectMilestoneFactory.create(owner=project_1)

    project_2 = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=project_2
    )

    milestone_3 = ProjectMilestoneFactory.create(owner=project_2)

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(
        Milestone.objects.all(), user
    )

    assert queryset.count() == 3
    assert set(queryset) == {milestone_1, milestone_2, milestone_3}


def test_groups(user):
    group_1 = ProjectGroupFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=group_1
    )

    milestone_1 = ProjectMilestoneFactory.create(owner=group_1)
    milestone_2 = ProjectMilestoneFactory.create(owner=group_1)

    group_2 = ProjectGroupFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=group_2
    )

    milestone_3 = ProjectMilestoneFactory.create(owner=group_2)

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(
        Milestone.objects.all(), user
    )

    assert queryset.count() == 3
    assert set(queryset) == {milestone_1, milestone_2, milestone_3}


def test_group_and_projects(user):
    group = ProjectGroupFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=group
    )

    milestone_1 = ProjectMilestoneFactory.create(owner=group)
    milestone_2 = ProjectMilestoneFactory.create(owner=group)

    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=project
    )

    milestone_3 = ProjectMilestoneFactory.create(owner=project)

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(
        Milestone.objects.all(), user
    )

    assert queryset.count() == 3
    assert set(queryset) == {milestone_1, milestone_2, milestone_3}


def test_group_with_projects(user):
    group = ProjectGroupFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=group
    )

    milestone_1 = ProjectMilestoneFactory.create(owner=group)
    milestone_2 = ProjectMilestoneFactory.create(owner=group)

    project_1 = ProjectFactory.create(group=group)
    project_2 = ProjectFactory.create(group=group)

    milestone_3 = ProjectMilestoneFactory.create(owner=project_1)
    milestone_4 = ProjectMilestoneFactory.create(owner=project_2)

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(
        Milestone.objects.all(), user
    )

    assert queryset.count() == 4
    assert set(queryset) == {milestone_1, milestone_2,
                             milestone_3, milestone_4}


def test_parent_group_with_groups(user):
    parent_group = ProjectGroupFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=parent_group
    )

    group_1 = ProjectGroupFactory.create(parent=parent_group)
    group_2 = ProjectGroupFactory.create(parent=parent_group)

    milestone_1 = ProjectMilestoneFactory.create(owner=group_1)
    milestone_2 = ProjectMilestoneFactory.create(owner=group_1)
    milestone_3 = ProjectMilestoneFactory.create(owner=group_2)

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(
        Milestone.objects.all(), user
    )

    assert queryset.count() == 3
    assert set(queryset) == {milestone_1, milestone_2, milestone_3}


def test_parent_group_with_groups_and_projects(user):
    parent_group = ProjectGroupFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=parent_group
    )

    group_1 = ProjectGroupFactory.create(parent=parent_group)
    group_2 = ProjectGroupFactory.create(parent=parent_group)

    milestone_1 = ProjectMilestoneFactory.create(owner=group_1)
    milestone_2 = ProjectMilestoneFactory.create(owner=group_2)

    project_1 = ProjectFactory.create(group=parent_group)
    project_2 = ProjectFactory.create(group=group_1)
    project_3 = ProjectFactory.create(group=group_2)

    milestone_3 = ProjectMilestoneFactory.create(owner=project_1)
    milestone_4 = ProjectMilestoneFactory.create(owner=project_2)
    milestone_5 = ProjectMilestoneFactory.create(owner=project_3)

    ProjectMilestoneFactory.create_batch(10)

    queryset = filter_allowed_for_user(Milestone.objects.all(), user)

    assert queryset.count() == 5
    assert set(queryset) == {milestone_1, milestone_2, milestone_3,
                             milestone_4, milestone_5}
