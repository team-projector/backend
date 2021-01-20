from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.core.application.use_cases import BasePresenter, BaseUseCase
from apps.core.gitlab import get_gitlab_client
from apps.development.models import Issue, Milestone, Project
from apps.development.services.errors import NoPersonalGitLabToken
from apps.development.services.issue.gl.manager import IssueGlManager
from apps.users.models import User


@dataclass(frozen=True)
class IssueCreateData:
    """Create issue data."""

    title: str
    project: int
    milestone: Optional[int]
    user: int
    labels: Optional[List[str]]
    estimate: Optional[int]
    due_date: date


@dataclass(frozen=True)
class InputDto:
    """Create issue input dto."""

    user: User
    data: IssueCreateData  # noqa: IssueCreateData


@dataclass(frozen=True)
class OutputDto:
    """Create issue output dto."""

    issue: Issue


class InputDtoValidator(serializers.Serializer):
    """InputSerializer."""

    title = serializers.CharField()
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects)
    milestone = serializers.PrimaryKeyRelatedField(
        queryset=Milestone.objects,
        allow_null=True,
    )
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)
    labels = serializers.ListField(
        child=serializers.CharField(),
        allow_null=True,
    )
    estimate = serializers.IntegerField(allow_null=True)
    due_date = serializers.DateField()

    def validate_estimate(self, estimate) -> int:
        """Validate estimate."""
        estimate = estimate or 0

        if estimate < 0:
            raise serializers.ValidationError(
                _("MSG__ESTIMATE_MUST_BE_MORE_0"),
            )

        return estimate

    def validate_due_date(self, due_date):  # noqa: N802
        """Validate due date. Date should not be in the past."""
        if due_date < datetime.now().date():
            raise serializers.ValidationError(
                _("MSG__DUE_DATE_SHOULD_NOT_BE_IN_THE_PAST"),
            )

        return due_date


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

        gl_client = get_gitlab_client(gl_token)

        validated_data = self.validate_input(input_dto.data, InputDtoValidator)

        gl_project = gl_client.projects.get(validated_data["project"].gl_id)
        gl_issue = gl_project.issues.create(
            self._prepare_new_issue_request_body(validated_data),
        )

        if validated_data["estimate"]:
            gl_issue.time_estimate("{0}s".format(validated_data["estimate"]))

        IssueGlManager().update_project_issue(
            validated_data["project"],
            gl_project,
            gl_issue,
        )

        self._presenter.present(
            OutputDto(issue=Issue.objects.get(gl_id=gl_issue.id)),
        )

    def _prepare_new_issue_request_body(self, issue_data) -> Dict[str, object]:
        request_body = {
            "title": issue_data["title"],
            "assignee_ids": [issue_data["user"].gl_id],
            "due_date": str(issue_data["due_date"]),
        }

        if issue_data["milestone"]:
            request_body["milestone_id"] = issue_data["milestone"].gl_id

        if issue_data["labels"]:
            request_body["labels"] = ",".join(issue_data["labels"])

        return request_body
