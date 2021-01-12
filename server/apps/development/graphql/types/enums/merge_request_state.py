import graphene

from apps.development.models.merge_request import (
    MergeRequestState as ModelMergeRequestState,
)

MergeRequestState = graphene.Enum.from_enum(ModelMergeRequestState)
