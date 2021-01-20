from dataclasses import dataclass

from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied
from rest_framework import serializers

from apps.core.application.errors import AccessDeniedApplicationError
from apps.core.application.use_cases import BaseUseCase
from apps.development.models import Milestone, Project, ProjectGroup
from apps.development.services.milestone.allowed import filter_allowed_for_user
from apps.development.tasks import (
    sync_project_group_milestone_task,
    sync_project_milestone_task,
)
from apps.users.models import User


@dataclass(frozen=True)
class MilestoneSyncData:
    """Sync milestone data."""

    milestone: int


@dataclass(frozen=True)
class InputDto:
    """Sync milestone input dto."""

    user: User
    data: MilestoneSyncData  # noqa: WPS110


@dataclass(frozen=True)
class OutputDto:
    """Sync milestone output dto."""

    milestone: Milestone


class InputDtoValidator(serializers.Serializer):
    """InputSerializer."""

    milestone = serializers.PrimaryKeyRelatedField(
        queryset=Milestone.objects.all(),
    )


class UseCase(BaseUseCase[InputDto, OutputDto]):
    """Usecase for updating milestones."""

    def execute(self, input_dto: InputDto) -> OutputDto:
        """Main logic here."""
        validated_data = self.validate_input(input_dto.data, InputDtoValidator)

        milestone = validated_data["milestone"]
        self._check_permissions(input_dto.user, milestone)

        if milestone.content_type.model_class() == Project:
            sync_project_milestone_task(
                milestone.owner.gl_id,
                milestone.gl_id,
            )
        elif milestone.content_type.model_class() == ProjectGroup:
            sync_project_group_milestone_task(
                milestone.owner.gl_id,
                milestone.gl_id,
            )

        return OutputDto(milestone=milestone)

    def _check_permissions(self, user: User, milestone: Milestone):
        try:
            allowed_milestone_qs = filter_allowed_for_user(
                Milestone.objects.filter(pk=milestone.pk),
                user,
            )
        except GraphQLPermissionDenied:  # noqa:WPS329
            raise AccessDeniedApplicationError
        else:
            if not allowed_milestone_qs.exists():
                raise AccessDeniedApplicationError
