from datetime import datetime

import factory

from tests.helpers.gitlab import gl_format_date, gl_format_datetime


class GlGroupMilestoneFactory(factory.DictFactory):
    id = factory.Faker("random_int")
    iid = factory.Faker("random_int")
    web_url = factory.Faker("url")
    group_id = factory.Faker("random_int")
    title = factory.Sequence(lambda seq: "Milestone {0}".format(seq))
    description = factory.Faker("word")
    start_date = gl_format_date(datetime.now())
    due_date = gl_format_date(datetime.now())
    created_at = gl_format_datetime(datetime.now())
    updated_at = gl_format_datetime(datetime.now())
    state = "active"
