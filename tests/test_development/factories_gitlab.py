from datetime import datetime
import factory

from apps.development.services.parsers import GITLAB_DATETIME_FORMAT, GITLAB_DATE_FORMAT


def gl_format_date(date):
    return str(date.strftime(GITLAB_DATE_FORMAT))


def gl_format_datetime(dt):
    return str(dt.strftime(GITLAB_DATETIME_FORMAT))


class GlGroupFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    web_url = factory.Faker('url')
    name = factory.Sequence(lambda n: f'Group {n}')
    full_name = factory.Sequence(lambda n: f'Test / Group {n}')
    description = factory.Faker('word')
    parent_id = None


class GlGroupMilestoneFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    iid = factory.Faker('random_int')
    web_url = factory.Faker('url')
    group_id = factory.Faker('random_int')
    title = factory.Sequence(lambda n: f'Milestone {n}')
    description = factory.Faker('word')
    start_date = gl_format_date(datetime.now())
    due_date = gl_format_date(datetime.now())
    created_at = gl_format_datetime(datetime.now())
    updated_at = gl_format_datetime(datetime.now())
    state = 'active'


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


class GlProjectMilestoneFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    iid = factory.Faker('random_int')
    web_url = factory.Faker('url')
    group_id = factory.Faker('random_int')
    title = factory.Sequence(lambda n: f'Milestone {n}')
    description = factory.Faker('word')
    start_date = gl_format_date(datetime.now())
    due_date = gl_format_date(datetime.now())
    created_at = gl_format_datetime(datetime.now())
    updated_at = gl_format_datetime(datetime.now())
    state = 'active'


class GlUserFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    name = factory.Sequence(lambda n: f'User {n}')
    username = factory.Sequence(lambda n: f'user_name{n}')
    state = 'active'


class GlProjectsIssueFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    iid = factory.Faker('random_int')
    web_url = factory.Faker('url')
    title = factory.Sequence(lambda n: f'Issue {n}')
    project_id = factory.Faker('random_int')
    state = 'opened'
    due_date = gl_format_date(datetime.now())
    created_at = gl_format_datetime(datetime.now())
    updated_at = gl_format_datetime(datetime.now())
    closed_at = gl_format_datetime(datetime.now())
    assignee = factory.SubFactory(GlUserFactory)
    milestone = None
    labels = []


class GlIssueTimeStats(factory.DictFactory):
    total_time_spent = factory.Faker('random_int')
    time_estimate = factory.Faker('random_int')


class GlHookFactory(factory.DictFactory):
    url = factory.Faker('url')


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
