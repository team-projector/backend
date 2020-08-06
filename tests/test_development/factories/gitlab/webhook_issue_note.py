# -*- coding: utf-8 -*-

import factory

from tests.test_development.factories.gitlab import GlNoteFactory
from tests.test_development.factories.gitlab.issue import GlIssueFactory
from tests.test_development.factories.gitlab.project import GlProjectFactory
from tests.test_users.factories.gitlab import GlUserFactory


class GlIssueNoteWebhookFactory(factory.DictFactory):
    """Gitlab issue note webhook factory."""

    object_kind = "note"
    event_type = "note"
    user = factory.SubFactory(GlUserFactory)
    project = factory.SubFactory(GlProjectFactory)
    issue = factory.SubFactory(GlIssueFactory)
    object_attributes = factory.SubFactory(GlNoteFactory)
