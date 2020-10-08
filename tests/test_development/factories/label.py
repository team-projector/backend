import factory

from apps.development.models import Label


class LabelFactory(factory.django.DjangoModelFactory):
    """Label factory."""

    class Meta:
        model = Label

    title = factory.Faker("text", max_nb_chars=200)
    color = factory.Faker("text", max_nb_chars=10)
