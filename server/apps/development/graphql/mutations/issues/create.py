from typing import Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.development.graphql.types import IssueType
from apps.development.use_cases.issues import create as issue_create


class CreateIssueMutation(BaseUseCaseMutation):
    """Create issue mutation."""

    class Meta:
        use_case_class = issue_create.UseCase
        permission_classes = (AllowAuthenticated,)

    class Arguments:
        title = graphene.String(required=True)
        project = graphene.ID(required=True)
        milestone = graphene.ID()
        user = graphene.ID(required=True)
        labels = graphene.List(graphene.String)
        estimate = graphene.Int()
        due_date = graphene.Date(required=True)

    issue = graphene.Field(IssueType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return issue_create.InputDto(
            user=info.context.user,  # type: ignore
            data=issue_create.IssueCreateData(
                title=kwargs["title"],
                project=kwargs["project"],
                milestone=kwargs.get("milestone"),
                user=kwargs["user"],
                labels=kwargs.get("labels"),
                estimate=kwargs.get("estimate"),
                due_date=kwargs["due_date"],
            ),
        )

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto: issue_create.OutputDto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "issue": output_dto.issue,
        }
