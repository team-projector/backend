import factory


class GlIssueAddSpentTimeFactory(factory.DictFactory):
    """Gitlab issue add spent time factory."""

    time_estimate = factory.Faker("random_int")
    total_time_spent = factory.Faker("random_int")
    human_time_estimate = factory.Faker("word")
    human_total_time_spent = factory.Faker("word")
