from dataclasses import dataclass

from rest_framework import serializers

from apps.core.application.errors import AccessDeniedApplicationError
from apps.core.application.use_cases import BaseUseCase
from apps.payroll.models.work_break import WorkBreak
from apps.payroll.services import work_break as work_break_service
from apps.payroll.services.work_break.allowed import (
    can_approve_decline_work_breaks,
)
from apps.users.models import User


@dataclass(frozen=True)
class ApproveWorkBreakData:
    """Approve work break data."""

    work_break: int


@dataclass(frozen=True)
class InputDto:
    """Approve work break input dto."""

    user: User
    data: ApproveWorkBreakData  # noqa: WPS110


@dataclass(frozen=True)
class OutputDto:
    """Approve work break output dto."""

    work_break: WorkBreak


class InputDtoValidator(serializers.Serializer):
    """InputSerializer."""

    work_break = serializers.PrimaryKeyRelatedField(
        queryset=WorkBreak.objects.all(),
    )


class UseCase(BaseUseCase[InputDto, OutputDto]):
    """Usecase for create workbreaks."""

    def execute(self, input_dto: InputDto) -> OutputDto:
        """Main logic here."""
        validated_data = self.validate_input(input_dto.data, InputDtoValidator)
        work_break = validated_data["work_break"]

        if not can_approve_decline_work_breaks(work_break, input_dto.user):
            raise AccessDeniedApplicationError()

        work_break_service.Manager(work_break).approve(
            approved_by=input_dto.user,
        )

        return OutputDto(work_break=work_break)
