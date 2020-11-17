from typing import Iterable

from apps.development.models import Project
from apps.development.models.project_member import ProjectMemberRole
from apps.users.models import User


def get_project_managers(project: Project) -> Iterable[User]:
    """Get managers related with the project."""
    if not project:
        return []

    managers = set()
    managers.update(
        member.user
        for member in project.members.filter(role=ProjectMemberRole.MANAGER)
    )

    parent = project.group
    while parent:
        managers.update(
            member.user
            for member in parent.members.filter(role=ProjectMemberRole.MANAGER)
        )
        parent = parent.parent

    return list(managers)
