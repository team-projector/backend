import factory


class GlUserFactory(factory.DictFactory):
    id = factory.Sequence(lambda i: i)
    name = factory.Sequence(lambda n: f'User {n}')
    username = factory.Sequence(lambda n: f'user_name{n}')
    state = 'active'


class GlProjectFactory(factory.DictFactory):
    id = factory.Sequence(lambda i: i)
    description = factory.Faker('word')
    name = factory.Sequence(lambda n: f'Project {n}')
    web_url = factory.Faker('url')
    name_with_namespace = factory.Faker('word')


class GlProjectsIssueFactory(factory.DictFactory):
    id = factory.Sequence(lambda i: i)
    iid = factory.Sequence(lambda i: i)
    project_id = factory.Sequence(lambda i: i)


class GlIssueAddSpentTimeFactory(factory.DictFactory):
    time_estimate = factory.Faker('random_int')
    total_time_spent = factory.Faker('random_int')
    human_time_estimate = factory.Faker('word')
    human_total_time_spent = factory.Faker('word')
