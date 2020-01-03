import factory


class GlHookFactory(factory.DictFactory):
    url = factory.Faker("url")
    issues_events = False
    merge_requests_events = False
