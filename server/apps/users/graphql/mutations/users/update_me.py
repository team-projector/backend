from typing import Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.users.graphql.types import UserType
from apps.users.logic.use_cases.me import update as me_update


class UpdateMeInput(graphene.InputObjectType):
    """Input for updating profile."""

    name = graphene.String()
    email = graphene.String()
    gl_token = graphene.String()


class UpdateMeMutation(BaseUseCaseMutation):
    """Update me user mutation."""

    class Meta:
        use_case_class = me_update.UseCase
        auth_required = True

    class Arguments:
        input = graphene.Argument(UpdateMeInput)  # noqa: WPS125

    me = graphene.Field(UserType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return me_update.InputDto(
            user=info.context.user,  # type: ignore
            data=me_update.MeUpdateData(**kwargs.get("input")),
        )

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto: me_update.OutputDto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "me": output_dto.user,
        }
