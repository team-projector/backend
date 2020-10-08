from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation

from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.graphql.mutations.tickets.inputs import DeleteTicketInput


class DeleteTicketMutation(SerializerMutation):
    """Delete ticket."""

    class Meta:
        serializer_class = DeleteTicketInput

    permission_classes = (AllowProjectManager,)

    ok = graphene.Boolean()

    @classmethod
    def perform_mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> "DeleteTicketMutation":
        """Perform mutation implementation."""
        validated_data["ticket"].delete()

        return cls(ok=True)
