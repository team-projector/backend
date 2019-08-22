import graphene
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.graphql.types import FeatureType
from apps.development.models import Feature, Milestone


class CreateFeatureMutation(BaseMutation):
    permission_classes = (AllowProjectManager,)

    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        start_date = graphene.Date(required=True)
        due_date = graphene.Date(required=True)
        milestone = graphene.ID(required=True)

    feature = graphene.Field(FeatureType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        milestone = get_object_or_404(
            Milestone.objects.all(),
            pk=kwargs['milestone']
        )

        kwargs['milestone'] = milestone
        feature = Feature.objects.create(**kwargs)

        return CreateFeatureMutation(feature=feature)


class UpdateFeatureMutation(BaseMutation):
    permission_classes = (AllowProjectManager,)

    class Arguments:
        id = graphene.ID()
        title = graphene.String()
        description = graphene.String()
        start_date = graphene.Date()
        due_date = graphene.Date()
        milestone = graphene.ID()

    feature = graphene.Field(FeatureType)

    @classmethod
    def do_mutate(cls, root, info, id, **kwargs):
        feature = get_object_or_404(
            Feature.objects.all(),
            pk=id
        )

        if kwargs.get('milestone'):
            milestone = get_object_or_404(
                Milestone.objects.all(),
                pk=kwargs['milestone']
            )

            kwargs['milestone'] = milestone

        for attr, value in kwargs.items():
            setattr(feature, attr, value)
        feature.save()

        return UpdateFeatureMutation(feature=feature)
