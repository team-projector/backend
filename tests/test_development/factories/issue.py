import factory
import pytz

from apps.development.models import Issue
from apps.development.models.issue import IssueState
from tests.test_development.factories.mixins.gl_field import GitlabFieldMixin
from tests.test_development.factories.project import ProjectFactory


class IssueFactory(GitlabFieldMixin):
    """Issue factory."""

    class Meta:
        model = Issue

    gl_iid = factory.Sequence(lambda seq: seq)
    title = factory.Faker("sentence")
    project = factory.SubFactory(ProjectFactory)
    time_estimate = factory.Faker("random_int", min=1, max=1000)
    total_time_spent = factory.Faker("random_int")
    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
    state = IssueState.OPENED
