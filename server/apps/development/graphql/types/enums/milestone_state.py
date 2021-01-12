import graphene

from apps.development.models.milestone import (
    MilestoneState as ModelMilestoneState,
)

MilestoneState = graphene.Enum.from_enum(ModelMilestoneState)
