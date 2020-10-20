import factory

from apps.skills.models import Position


class PositionFactory(factory.django.DjangoModelFactory):
    """Position factory."""

    class Meta:
        model = Position

    title = factory.Faker("word")
