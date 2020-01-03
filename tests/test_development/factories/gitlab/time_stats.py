import factory


class GlTimeStats(factory.DictFactory):
    total_time_spent = factory.Faker("random_int")
    time_estimate = factory.Faker("random_int")
