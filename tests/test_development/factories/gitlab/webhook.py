import factory


class GlHookFactory(factory.DictFactory):
    """Gitlab hook factory."""

    url = factory.Faker("url")
    issues_events = False
    merge_requests_events = False
