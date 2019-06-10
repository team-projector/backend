import factory


class GlGroupFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    web_url = factory.Faker('url')
    name = factory.Sequence(lambda n: f'Group {n}')
    full_name = factory.Sequence(lambda n: f'Test / Group {n}')
    parent_id = None


class GlIssueAddSpentTimeFactory(factory.DictFactory):
    time_estimate = factory.Faker('random_int')
    total_time_spent = factory.Faker('random_int')
    human_time_estimate = factory.Faker('word')
    human_total_time_spent = factory.Faker('word')


class GlProjectFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    description = factory.Faker('word')
    name = factory.Sequence(lambda n: f'Project {n}')
    web_url = factory.Faker('url')
    name_with_namespace = factory.Faker('word')


class GlProjectsIssueFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    iid = factory.Faker('random_int')
    project_id = factory.Faker('random_int')


class GlUserFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    name = factory.Sequence(lambda n: f'User {n}')
    username = factory.Sequence(lambda n: f'user_name{n}')
    state = 'active'


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
