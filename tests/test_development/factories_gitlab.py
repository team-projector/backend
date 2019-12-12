from datetime import datetime

import factory
from apps.core.gitlab.parsers import GITLAB_DATE_FORMAT, GITLAB_DATETIME_FORMAT


def gl_format_date(date):
    return str(date.strftime(GITLAB_DATE_FORMAT))


def gl_format_datetime(dt):
    return str(dt.strftime(GITLAB_DATETIME_FORMAT))


class GlGroupFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    web_url = factory.Faker('url')
    avatar_url = factory.Faker('url')
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
    avatar_url = factory.Faker('url')
    name_with_namespace = factory.Faker('word')
    archived = False


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
    public_email = factory.Sequence(lambda n: f'public.email{n}@test.com')
    username = factory.Sequence(lambda n: f'user_name{n}')
    state = 'active'
    avatar_url = factory.Faker('url')
    web_url = factory.Faker('url')


class GlIssueFactory(factory.DictFactory):
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


class GlTimeStats(factory.DictFactory):
    total_time_spent = factory.Faker('random_int')
    time_estimate = factory.Faker('random_int')


class GlHookFactory(factory.DictFactory):
    url = factory.Faker('url')
    issues_events = False
    merge_requests_events = False


class GlNoteFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    body = factory.Faker('word')
    created_at = gl_format_datetime(datetime.now())
    updated_at = gl_format_datetime(datetime.now())
    author = factory.SubFactory(GlUserFactory)


class GlLabelFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    name = factory.Faker('word')
    color = factory.Faker('text', max_nb_chars=10)


class GlMergeRequestFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    iid = factory.Faker('random_int')
    web_url = factory.Faker('url')
    title = factory.Sequence(lambda n: f'MergeRequest {n}')
    project_id = factory.Faker('random_int')
    state = 'opened'
    due_date = gl_format_date(datetime.now())
    created_at = gl_format_datetime(datetime.now())
    updated_at = gl_format_datetime(datetime.now())
    closed_at = gl_format_datetime(datetime.now())
    assignee = factory.SubFactory(GlUserFactory)
    milestone = None
    labels = []


class GlIssueWebhookFactory(factory.DictFactory):
    object_kind = 'issue'
    event_type = 'issue'
    user = factory.SubFactory(GlUserFactory)
    project = factory.SubFactory(GlProjectFactory)
    object_attributes = factory.SubFactory(GlIssueFactory)


class GlMergeRequestWebhookFactory(factory.DictFactory):
    object_kind = 'merge_request'
    event_type = 'merge_request'
    user = factory.SubFactory(GlUserFactory)
    project = factory.SubFactory(GlProjectFactory)
    object_attributes = factory.SubFactory(GlMergeRequestFactory)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
