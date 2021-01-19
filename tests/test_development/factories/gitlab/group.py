import factory


class GlGroupFactory(factory.DictFactory):
    """Gitlab group factory."""

    id = factory.Faker("random_int")  # noqa: WPS125
    web_url = factory.Faker("url")
    avatar_url = factory.Faker("url")
    name = factory.Sequence(lambda seq: "Group {0}".format(seq))
    full_name = factory.Sequence(lambda seq: "Test / Group {0}".format(seq))
    description = factory.Faker("word")
    parent_id = None
