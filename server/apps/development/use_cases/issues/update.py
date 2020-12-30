from dataclasses import dataclass

from django.db import transaction
from rest_framework import serializers

from apps.core.application.errors import AccessDeniedApplicationError
from apps.core.application.use_cases import BasePresenter, BaseUseCase
from apps.development.models import Issue, Ticket
from apps.development.services.issue.allowed import filter_allowed_for_user
from apps.development.tasks import propagate_ticket_to_related_issues_task
from apps.users.models import User


@dataclass(frozen=True)
class IssueUpdateData:
    """Update issue data."""

    issue: int
    ticket: int


@dataclass(frozen=True)
class InputDto:
    """Update issue input dto."""

    user: User
    data: IssueUpdateData  # noqa: IssueUpdateData


@dataclass(frozen=True)
class OutputDto:
    """Update issue output dto."""

    issue: Issue


class InputDtoSerializer(serializers.Serializer):
    """InputSerializer."""

    class Meta:
        model = Issue

    issue = serializers.PrimaryKeyRelatedField(
        queryset=Issue.objects.all(),
    )
    ticket = serializers.PrimaryKeyRelatedField(
        queryset=Ticket.objects.all(),
    )


class UseCase(BaseUseCase):
    """Usecase for updating issues."""

    def __init__(self, presenter: BasePresenter):
        """Initialize."""
        self._presenter = presenter

    def execute(self, input_dto: InputDto) -> None:
        """Main logic here."""
        validated_data = self.validate_input(
            input_dto.data,
            InputDtoSerializer,
        )

        issue = validated_data["issue"]
        self._check_permissions(input_dto.user, issue)

        issue.ticket = validated_data["ticket"]
        issue.save()

        transaction.on_commit(
            lambda: propagate_ticket_to_related_issues_task(issue).delay(
                issue_id=issue.pk,
            ),
        )

        self._presenter.present(OutputDto(issue=issue))

    def _check_permissions(self, user: User, issue: Issue):
        allowed_for_user = filter_allowed_for_user(
            Issue.objects.filter(id=issue.id),
            user,
        )

        if allowed_for_user.exists():
            return

        raise AccessDeniedApplicationError
