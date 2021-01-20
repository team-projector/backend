from dataclasses import dataclass

from rest_framework import serializers

from apps.core.application.use_cases import BasePresenter, BaseUseCase
from apps.development.models import Issue
from apps.development.services.errors import NoPersonalGitLabToken
from apps.development.services.issue.allowed import check_permissions
from apps.payroll.services.spent_time.gitlab import add_spent_time
from apps.users.models import User


@dataclass(frozen=True)
class AddSpentTimeData:
    """Add spent time to issue data."""

    issue: int
    seconds: int


@dataclass(frozen=True)
class InputDto:
    """Add spent time to issue input dto."""

    user: User
    data: AddSpentTimeData  # noqa: WPS110


@dataclass(frozen=True)
class OutputDto:
    """Add spent time to issue output dto."""

    issue: Issue


class InputDtoValidator(serializers.Serializer):
    """InputSerializer."""

    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())
    seconds = serializers.IntegerField(min_value=1)


class UseCase(BaseUseCase):
    """Usecase for updating issues."""

    def __init__(self, presenter: BasePresenter):
        """Initialize."""
        self._presenter = presenter

    def execute(self, input_dto: InputDto) -> None:
        """Main logic here."""
        gl_token = input_dto.user.gl_token
        if not gl_token:
            raise NoPersonalGitLabToken

        validated_data = self.validate_input(input_dto.data, InputDtoValidator)

        issue = validated_data["issue"]
        check_permissions(input_dto.user, issue)

        add_spent_time(
            input_dto.user,
            validated_data["issue"],
            validated_data["seconds"],
        )

        self._presenter.present(OutputDto(issue=issue))
