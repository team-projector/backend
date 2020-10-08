import factory

from apps.development.models import Team


class TeamFactory(factory.django.DjangoModelFactory):
    """Team factory."""

    class Meta:
        model = Team

    title = factory.Faker("text", max_nb_chars=200)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        """Set members."""
        if create and extracted:
            self.members.set(extracted)
