from dataclasses import dataclass

from rest_framework import serializers

from apps.core.application.use_cases import BaseUseCase
from apps.development.models import Issue
from apps.development.services.issue.allowed import check_permissions
from apps.development.tasks import sync_project_issue_task
from apps.users.models import User


@dataclass(frozen=True)
class IssueSyncData:
    """Sync issue data."""

    issue: int


@dataclass(frozen=True)
class InputDto:
    """Sync issue input dto."""

    user: User
    data: IssueSyncData  # noqa: WPS110


@dataclass(frozen=True)
class OutputDto:
    """Sync issue output dto."""

    issue: Issue


class InputDtoValidator(serializers.Serializer):
    """InputSerializer."""

    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())


class UseCase(BaseUseCase[InputDto, OutputDto]):
    """Usecase for updating issues."""

    def execute(self, input_dto: InputDto) -> OutputDto:
        """Main logic here."""
        validated_data = self.validate_input(input_dto.data, InputDtoValidator)

        issue = validated_data["issue"]
        check_permissions(input_dto.user, issue)

        if issue.project:
            sync_project_issue_task.delay(
                issue.project.gl_id,
                issue.gl_iid,
            )

        return OutputDto(issue=issue)
