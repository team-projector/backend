# -*- coding: utf-8 -*-

import factory

from tests.test_development.factories.gitlab.merge_request import (
    GlMergeRequestFactory,
)
from tests.test_development.factories.gitlab.project import GlProjectFactory
from tests.test_users.factories.gitlab import GlUserFactory


class GlMergeRequestWebhookFactory(factory.DictFactory):
    object_kind = "merge_request"
    event_type = "merge_request"
    user = factory.SubFactory(GlUserFactory)
    project = factory.SubFactory(GlProjectFactory)
    object_attributes = factory.SubFactory(GlMergeRequestFactory)
