from datetime import datetime

import factory

from tests.helpers.gitlab import gl_format_date, gl_format_datetime
from tests.test_users.factories.gitlab import GlUserFactory


class GlMergeRequestFactory(factory.DictFactory):
    id = factory.Faker('random_int')
    iid = factory.Faker('random_int')
    web_url = factory.Faker('url')
    title = factory.Sequence(lambda seq: 'MergeRequest {0}'.format(seq))
    project_id = factory.Faker('random_int')
    state = 'opened'
    due_date = gl_format_date(datetime.now())
    created_at = gl_format_datetime(datetime.now())
    updated_at = gl_format_datetime(datetime.now())
    closed_at = gl_format_datetime(datetime.now())
    assignee = factory.SubFactory(GlUserFactory)
    milestone = None
    labels = []