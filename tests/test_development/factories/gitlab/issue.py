from datetime import datetime

import factory

from tests.helpers.gitlab import gl_format_date, gl_format_datetime
from tests.test_development.factories.gitlab.project_milestone import (
    GlProjectMilestoneFactory,
)
from tests.test_users.factories.gitlab import GlUserFactory


class GlIssueFactory(factory.DictFactory):
    """Gitlab issue factory."""

    id = factory.Faker("random_int")  # noqa: WPS125, A003
    iid = factory.Faker("random_int")
    web_url = factory.Faker("url")
    title = factory.Sequence(lambda seq: "Issue {0}".format(seq))
    project_id = factory.Faker("random_int")
    state = "opened"
    due_date = gl_format_date(datetime.now())
    created_at = gl_format_datetime(datetime.now())
    updated_at = gl_format_datetime(datetime.now())
    closed_at = gl_format_datetime(datetime.now())
    assignee = factory.SubFactory(GlUserFactory)
    labels = []
    milestone = factory.SubFactory(GlProjectMilestoneFactory)
    description = factory.Faker("text", max_nb_chars=50)
    author = None
