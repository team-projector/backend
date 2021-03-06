from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Optional

from rest_framework import serializers

from apps.core.application.use_cases import BaseUseCase
from apps.payroll.models.work_break import WorkBreak, WorkBreakReason
from apps.users.models import User


@dataclass(frozen=True)
class CreateWorkBreakData:
    """Update work break data."""

    comment: str
    from_date: date
    to_date: date
    reason: WorkBreakReason
    user: int
    paid_days: Optional[int]


@dataclass(frozen=True)
class InputDto:
    """Update workbreak input dto."""

    user: User
    data: CreateWorkBreakData  # noqa: WPS110


@dataclass(frozen=True)
class OutputDto:
    """Update workbreak output dto."""

    work_break: WorkBreak


class InputDtoValidator(serializers.Serializer):
    """InputSerializer."""

    comment = serializers.CharField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    reason = serializers.ChoiceField(choices=WorkBreakReason)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )
    paid_days = serializers.IntegerField(
        min_value=0,
        required=False,
        allow_null=True,
    )

    def validate(self, attrs) -> Dict[str, str]:
        """Validation attrs."""
        attrs = super().validate(attrs)
        self._fill_paid_days(attrs)
        return attrs

    def _fill_paid_days(self, attrs) -> None:
        if attrs.get("paid_days"):
            return

        current_year = datetime.now().year
        to_date = attrs.get("to_date")
        from_date = attrs.get("from_date")

        if to_date.year > current_year:
            to_date = date(current_year + 1, 1, 1)

        if from_date.year < current_year:
            from_date = date(current_year, 1, 1)

        attrs["paid_days"] = max(
            ((to_date - from_date).days, 0),
        )  # noqa: WPS601


class UseCase(BaseUseCase[InputDto, OutputDto]):
    """Usecase for create workbreaks."""

    def execute(self, input_dto: InputDto) -> OutputDto:
        """Main logic here."""
        validated_data = self.validate_input(input_dto.data, InputDtoValidator)

        work_break = WorkBreak()
        work_break.comment = validated_data["comment"]
        work_break.from_date = validated_data["from_date"]
        work_break.to_date = validated_data["to_date"]
        work_break.reason = validated_data["reason"]
        work_break.user = validated_data["user"]

        paid_days = validated_data["paid_days"]
        if paid_days is not None:
            work_break.paid_days = paid_days

        work_break.save()

        return OutputDto(work_break=work_break)
