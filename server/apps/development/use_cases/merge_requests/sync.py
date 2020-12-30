from dataclasses import dataclass

from rest_framework import serializers

from apps.core.application.use_cases import BasePresenter, BaseUseCase
from apps.development.models import MergeRequest
from apps.development.tasks import sync_project_merge_request_task


@dataclass(frozen=True)
class SyncMergeRequestInputDto:
    """Sync merge request input dto."""

    merge_request: int


@dataclass(frozen=True)
class SyncMergeRequestOutputDto:
    """Sync merge request output dto."""

    merge_request: MergeRequest


class InputDtoSerializer((serializers.Serializer)):
    """InputSerializer."""

    merge_request = serializers.PrimaryKeyRelatedField(
        queryset=MergeRequest.objects.all(),
    )


class SyncMergeRequestUseCase(BaseUseCase):
    """Usecase for updating merge requests."""

    def __init__(self, presenter: BasePresenter):
        """Initialize."""
        self._presenter = presenter

    def execute(self, input_dto: SyncMergeRequestInputDto) -> None:
        """Main logic here."""
        validated_data = self.validate_input(input_dto, InputDtoSerializer)

        merge_request = validated_data["merge_request"]
        if merge_request.project:
            sync_project_merge_request_task.delay(
                merge_request.project.gl_id,
                merge_request.gl_iid,
            )

        self._presenter.present(
            SyncMergeRequestOutputDto(
                merge_request=merge_request,
            ),
        )
