import graphene

from apps.development.models.project import ProjectState as ModelProjectState

ProjectState = graphene.Enum.from_enum(ModelProjectState)
