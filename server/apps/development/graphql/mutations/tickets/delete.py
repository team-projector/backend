from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied
from jnt_django_graphene_toolbox.mutations import BaseSerializerMutation
from rest_framework import serializers

from apps.core.graphql.mutations.base import BaseMutation
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


class DeleteTicketMutation(BaseMutation, BaseSerializerMutation):
    """Delete ticket."""

    class Meta:
        serializer_class = InputSerializer
        auth_required = True

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> "DeleteTicketMutation":
        """Perform mutation implementation."""
        if not info.context.user.is_project_manager:  # type: ignore
            raise GraphQLPermissionDenied()

        validated_data["ticket"].delete()

        return cls(ok=True)
