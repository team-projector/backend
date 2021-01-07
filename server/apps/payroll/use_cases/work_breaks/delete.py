from dataclasses import dataclass

from rest_framework import serializers

from apps.core.application.errors import AccessDeniedApplicationError
from apps.core.application.use_cases import BasePresenter, BaseUseCase
from apps.payroll.models.work_break import WorkBreak
from apps.payroll.services.work_break.allowed import can_manage_work_break
from apps.users.models import User


@dataclass(frozen=True)
class WorkBreakDeleteData:
    """Delete work break data."""

    work_break: int


@dataclass(frozen=True)
class InputDto:
    """Delete work break input dto."""

    data: WorkBreakDeleteData  # noqa: WPS110
    user: User


class InputDtoSerializer(serializers.Serializer):
    """InputSerializer."""

    work_break = serializers.PrimaryKeyRelatedField(
        queryset=WorkBreak.objects.all(),
    )


class UseCase(BaseUseCase):
    """Use case for declining work breaks."""

    def __init__(self, presenter: BasePresenter):
        """Initialize."""
        self._presenter = presenter

    def execute(self, input_dto: InputDto) -> None:
        """Main logic here."""
        validated_data = self.validate_input(
            input_dto.data,
            InputDtoSerializer,
        )

        work_break = validated_data["work_break"]
        if not can_manage_work_break(work_break, input_dto.user):
            raise AccessDeniedApplicationError()

        work_break.delete()
