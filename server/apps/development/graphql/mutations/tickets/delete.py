from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import BaseSerializerMutation
from rest_framework import serializers

from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.models import Ticket


class InputSerializer(serializers.Serializer):
    """InputSerializer."""

    id = serializers.PrimaryKeyRelatedField(  # noqa: WPS125, A003
        queryset=Ticket.objects.all(),
    )

    @property
    def validated_data(self):
        """Validated data changing."""
        validated_data = super().validated_data
        validated_data["ticket"] = validated_data.pop("id", None)
        return validated_data


class DeleteTicketMutation(BaseSerializerMutation):
    """Delete ticket."""

    class Meta:
        serializer_class = InputSerializer
        permission_classes = (AllowProjectManager,)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> "DeleteTicketMutation":
        """Perform mutation implementation."""
        validated_data["ticket"].delete()

        return cls(ok=True)
