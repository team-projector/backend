import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.development.graphql.filters import FeaturesFilterSet
from apps.development.graphql.types import FeatureType


class FeaturesQueries(graphene.ObjectType):
    all_features = DataSourceConnectionField(
        FeatureType,
        filterset_class=FeaturesFilterSet
    )
