from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from rest_framework import serializers

from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.models import Ticket


class _InputSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(  # noqa: WPS125, A003
        queryset=Ticket.objects.all(),
    )

    @property
    def validated_data(self):
        """Validated data changing."""
        ret = super().validated_data
        ret["ticket"] = ret.pop("id", None)
        return ret


class DeleteTicketMutation(SerializerMutation):
    """Delete ticket."""

    class Meta:
        serializer_class = _InputSerializer

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
