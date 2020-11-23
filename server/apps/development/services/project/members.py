from typing import Iterable

from django.db import models

from apps.development.models import Project
from apps.development.models.project_member import ProjectMember
from apps.users.models import User


def get_project_managers(project: Project) -> Iterable[User]:
    """Get managers related with the project."""
    if not project:
        return []

    query_manager = models.Q(roles=ProjectMember.roles.MANAGER)

    project_members = project.members.filter(query_manager).values("user_id")

    project_group = project.group
    while project_group:
        project_members = project_members.union(
            project_group.members.filter(query_manager).values("user_id"),
        )

        project_group = project_group.parent

    return list(User.objects.filter(id__in=project_members))
