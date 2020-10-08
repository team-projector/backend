import factory

from tests.test_development.factories.gitlab.issue import GlIssueFactory
from tests.test_development.factories.gitlab.project import GlProjectFactory
from tests.test_users.factories.gitlab import GlUserFactory


class GlIssueWebhookFactory(factory.DictFactory):
    """Gitlab issue webhook factory."""

    object_kind = "issue"
    event_type = "issue"
    user = factory.SubFactory(GlUserFactory)
    project = factory.SubFactory(GlProjectFactory)
    object_attributes = factory.SubFactory(GlIssueFactory)
