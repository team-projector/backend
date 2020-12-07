import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import Milestone
from apps.development.services.milestone.allowed import (
    filter_allowed_for_user,
    is_project_manager,
)
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
    ProjectMilestoneFactory,
)


def test_not_project_manager(project_developer, group_customer, group):
    """
    Test not project manager.

    :param project_developer:
    :param group_customer:
    :param group:
    """
    project = ProjectFactory.create()
    ProjectMilestoneFactory.create(owner=project)
    ProjectMilestoneFactory.create(owner=group)

    assert not filter_allowed_for_user(
        Milestone.objects.all(),
        project_developer,
    )


def test_not_project_member(user, project_developer, group_customer, group):
    """
    Test not project manager.

    :param user:
    :param project_developer:
    :param group_customer:
    :param group:
    """
    project = ProjectFactory.create()
    ProjectMilestoneFactory.create(owner=project)
    ProjectMilestoneFactory.create(owner=group)

    with pytest.raises(GraphQLPermissionDenied):
        filter_allowed_for_user(Milestone.objects.all(), user)


def test_is_project_manager(
    user,
    make_project_manager,
    make_group_manager,
):
    """Test is project manager."""
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

    for milestone in milestones:
        assert is_project_manager(user, milestone)
