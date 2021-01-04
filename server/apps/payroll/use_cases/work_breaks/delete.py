from dataclasses import dataclass

from rest_framework import serializers

from apps.core.application.use_cases import BasePresenter, BaseUseCase
from apps.payroll.models.work_break import WorkBreak


@dataclass(frozen=True)
class InputDto:
    """Delete work break input dto."""

    work_break: int


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
            input_dto,
            InputDtoSerializer,
        )

        work_break = validated_data["work_break"]
        work_break.delete()
