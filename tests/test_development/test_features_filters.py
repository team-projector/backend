from apps.development.graphql.filters import FeaturesFilterSet
from apps.development.models import Feature
from tests.test_development.factories import (
    FeatureFactory, ProjectMilestoneFactory,
)


def test_filter_by_milestone(user):
    milestone_1 = ProjectMilestoneFactory.create()
    FeatureFactory.create(milestone=milestone_1)

    milestone_2 = ProjectMilestoneFactory.create()
    FeatureFactory.create(milestone=milestone_2)

    results = FeaturesFilterSet(
        data={'milestone': milestone_1.id},
        queryset=Feature.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().milestone == milestone_1

    results = FeaturesFilterSet(
        data={'milestone': milestone_2.id},
        queryset=Feature.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().milestone == milestone_2
