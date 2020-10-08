import factory


class GlLabelFactory(factory.DictFactory):
    """Gitlab label factory."""

    id = factory.Faker("random_int")  # noqa: WPS125, A003
    name = factory.Faker("word")
    color = factory.Faker("text", max_nb_chars=10)
