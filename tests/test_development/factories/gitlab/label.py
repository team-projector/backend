import factory


class GlLabelFactory(factory.DictFactory):
    id = factory.Faker("random_int")
    name = factory.Faker("word")
    color = factory.Faker("text", max_nb_chars=10)
