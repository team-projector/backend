# -*- coding: utf-8 -*-

import factory
import pytz

from apps.development.models import MergeRequest
from apps.development.models.merge_request import MergeRequestState
from tests.test_development.factories.mixins.gl_field import GitlabFieldMixin
from tests.test_development.factories.project_group_milestone import (
    ProjectGroupMilestoneFactory,
)
from tests.test_users.factories import UserFactory


class MergeRequestFactory(GitlabFieldMixin):
    state = MergeRequestState.OPENED
    title = factory.Faker("text", max_nb_chars=200)
    time_estimate = factory.Faker("random_int")
    milestone = factory.SubFactory(ProjectGroupMilestoneFactory)
    gl_iid = factory.Sequence(lambda seq: seq)
    author = factory.SubFactory(UserFactory)
    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )

    class Meta:
        model = MergeRequest
