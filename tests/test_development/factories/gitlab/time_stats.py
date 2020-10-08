import factory


class GlTimeStats(factory.DictFactory):
    """Gitlab time stats."""

    total_time_spent = factory.Faker("random_int")
    time_estimate = factory.Faker("random_int")
