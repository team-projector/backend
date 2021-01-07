from dataclasses import dataclass
from datetime import date
from typing import Optional

from rest_framework import serializers

from apps.core.application.errors import AccessDeniedApplicationError
from apps.core.application.use_cases import BasePresenter, BaseUseCase
from apps.payroll.models.work_break import WorkBreak, WorkBreakReason
from apps.payroll.services.work_break.allowed import can_manage_work_break
from apps.payroll.use_cases.work_breaks.create import (
    InputDtoSerializer as CreateWorkBreakInputDtoSerializer,
)
from apps.users.models import User


@dataclass(frozen=True)
class UpdateWorkBreakData:
    """Update workbreak data."""

    work_break: int
    comment: str
    from_date: date
    to_date: date
    reason: WorkBreakReason
    user: int
    paid_days: Optional[int]


@dataclass(frozen=True)
class UpdateWorkBreakInputDto:
    """Update workbreak input dto."""

    user: User
    data: UpdateWorkBreakData  # noqa: WPS110


@dataclass(frozen=True)
class UpdateWorkBreakOutputDto:
    """Update workbreak output dto."""

    work_break: WorkBreak


class InputDtoSerializer(CreateWorkBreakInputDtoSerializer):
    """InputSerializer."""

    work_break = serializers.PrimaryKeyRelatedField(
        queryset=WorkBreak.objects.all(),
    )


class UpdateWorkBreakUseCase(BaseUseCase):
    """Usecase for updating workbreaks."""

    def __init__(self, presenter: BasePresenter):
        """Initialize."""
        self._presenter = presenter

    def execute(self, input_dto: UpdateWorkBreakInputDto) -> None:
        """Main logic here."""
        validated_data = self.validate_input(
            input_dto.data,
            InputDtoSerializer,
        )

        work_break = validated_data["work_break"]
        if not can_manage_work_break(work_break, input_dto.user):
            raise AccessDeniedApplicationError()

        work_break.comment = validated_data["comment"]
        work_break.from_date = validated_data["from_date"]
        work_break.to_date = validated_data["to_date"]
        work_break.reason = validated_data["reason"]
        work_break.user = validated_data["user"]

        if validated_data["paid_days"] is not None:
            work_break.paid_days = validated_data["paid_days"]

        work_break.save()

        self._presenter.present(
            UpdateWorkBreakOutputDto(
                work_break=work_break,
            ),
        )
