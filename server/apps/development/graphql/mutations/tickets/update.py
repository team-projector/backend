from typing import Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.development.graphql.types import TicketType
from apps.development.models import ticket
from apps.development.use_cases.tickets import update as ticket_update


class UpdateTicketMutation(BaseUseCaseMutation):
    """Update ticket mutation."""

    class Meta:
        use_case_class = ticket_update.UseCase
        auth_required = True

    class Arguments:
        id = graphene.ID(required=True)  # noqa: WPS125
        title = graphene.String()
        start_date = graphene.Date()
        due_date = graphene.Date()
        type = graphene.Argument(  # noqa: WPS125
            graphene.Enum.from_enum(ticket.TicketType),
        )
        state = graphene.Argument(graphene.Enum.from_enum(ticket.TicketState))
        issues = graphene.List(graphene.ID)
        attach_issues = graphene.List(graphene.ID)
        role = graphene.String()
        url = graphene.String()
        estimate = graphene.Int()
        milestone = graphene.ID()

    ticket = graphene.Field(TicketType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return ticket_update.InputDto(
            user=info.context.user,  # type: ignore
            data=ticket_update.TicketUpdateData(
                ticket=kwargs["id"],
                title=kwargs.get("title"),
                start_date=kwargs.get("start_date"),
                due_date=kwargs.get("due_date"),
                type=kwargs.get("type"),
                state=kwargs.get("state"),
                issues=kwargs.get("issues", []),
                attach_issues=kwargs.get("attach_issues", []),
                role=kwargs.get("role"),
                url=kwargs.get("url"),
                estimate=kwargs.get("estimate") or 0,
                milestone=kwargs.get("milestone"),
            ),
            fields_to_update=list(kwargs.keys()),
        )

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto: ticket_update.OutputDto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "ticket": output_dto.ticket,
        }
