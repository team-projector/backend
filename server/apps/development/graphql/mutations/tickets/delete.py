from typing import Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.development.use_cases.tickets import delete as ticket_delete


class DeleteTicketMutation(BaseUseCaseMutation):
    """Delete ticket mutation."""

    class Meta:
        use_case_class = ticket_delete.UseCase
        auth_required = True

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003 WPS125

    ok = graphene.Boolean()

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return ticket_delete.InputDto(
            user=info.context.user,  # type: ignore
            data=ticket_delete.TicketDeleteData(
                ticket=kwargs["id"],
            ),
        )

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "ok": True,
        }
