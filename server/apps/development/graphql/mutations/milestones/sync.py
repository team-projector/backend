from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.development.graphql.types import MilestoneType
from apps.development.models import Milestone, Project, ProjectGroup
from apps.development.services.milestone.allowed import filter_allowed_for_user
from apps.development.tasks import (
    sync_project_group_milestone_task,
    sync_project_milestone_task,
)


class InputSerializer(serializers.ModelSerializer):
    """InputSerializer."""

    class Meta:
        model = Milestone
        fields = ("id",)

    id = serializers.PrimaryKeyRelatedField(  # noqa:WPS125, A003
        queryset=Milestone.objects.all(),
    )

    @property
    def validated_data(self):
        """Validated data changing."""
        validated_data = super().validated_data
        validated_data["milestone"] = validated_data.pop("id", None)
        return validated_data

    def validate_id(self, milestone):
        """Validates that user have permissions to mutate milestone."""
        if not milestone:
            return None

        err = ValidationError(
            "You don't have permissions to mutate this milestone",
        )

        try:
            allowed_milestone_qs = filter_allowed_for_user(
                Milestone.objects.filter(id=milestone.id),
                self.context["request"].user,
            )
        except GraphQLPermissionDenied:  # noqa:WPS329
            raise err
        else:
            if not allowed_milestone_qs.exists():
                raise err

        return milestone


class SyncMilestoneMutation(SerializerMutation):
    """Syncing milestone mutation."""

    class Meta:
        serializer_class = InputSerializer
        permission_classes = (AllowAuthenticated,)

    milestone = graphene.Field(MilestoneType)

    @classmethod
    def mutate_and_get_payload(  # type: ignore
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110ø
        validated_data: Dict[str, Any],
    ) -> "SyncMilestoneMutation":
        """Syncing milestone."""
        milestone = validated_data.pop("milestone")

        if milestone.content_type.model_class() == Project:
            sync_project_milestone_task(
                milestone.owner.gl_id,
                milestone.gl_id,
            )
        elif milestone.content_type.model_class() == ProjectGroup:
            sync_project_group_milestone_task(
                milestone.owner.gl_id,
                milestone.gl_id,
            )

        return cls(milestone=milestone)
