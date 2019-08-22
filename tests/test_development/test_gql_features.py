from datetime import datetime
from pytest import raises
from django.core.exceptions import PermissionDenied

from apps.development.graphql.mutations.features import (
    CreateFeatureMutation, UpdateFeatureMutation
)
from apps.development.graphql.types.feature import FeatureType
from apps.development.models import Feature
from apps.users.models import User
from tests.test_development.factories import (
    FeatureFactory, ProjectMilestoneFactory
)
from tests.test_development.factories_gitlab import AttrDict


def test_features(user, client):
    user.roles = User.roles.project_manager
    user.save()

    FeatureFactory.create_batch(5)

    client.user = user
    info = AttrDict({'context': client})

    features = FeatureType().get_queryset(Feature.objects.all(), info)

    assert features.count() == 5


def test_features_not_pm(user, client):
    FeatureFactory.create_batch(5)

    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        FeatureType().get_queryset(
            Feature.objects.all(), info
        )


def test_feature_create(user, client):
    user.roles = User.roles.project_manager
    user.save()

    client.user = user
    info = AttrDict({'context': client})

    milestone = ProjectMilestoneFactory.create()

    CreateFeatureMutation.do_mutate(
        None,
        info,
        title='test feature',
        description='description',
        start_date=str(datetime.now().date()),
        due_date=str(datetime.now().date()),
        milestone=milestone.id
    )

    assert Feature.objects.count() == 1
    assert Feature.objects.first().milestone == milestone


def test_feature_update(user, client):
    user.roles = User.roles.project_manager
    user.save()

    client.user = user
    info = AttrDict({'context': client})

    feature = FeatureFactory.create(description='created',
                                    milestone=ProjectMilestoneFactory.create())

    milestone = ProjectMilestoneFactory.create()

    UpdateFeatureMutation.do_mutate(
        None,
        info,
        feature.id,
        description='updated',
        milestone=milestone.id
    )

    assert Feature.objects.count() == 1
    assert Feature.objects.first().description == 'updated'
    assert Feature.objects.first().milestone == milestone
