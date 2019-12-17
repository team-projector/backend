import factory
import pytz

from apps.development.models import Issue
from apps.development.models.issue import ISSUE_STATES
from tests.test_development.factories.mixins.gl_field import GitlabFieldMixin
from tests.test_development.factories.project import ProjectFactory


class IssueFactory(GitlabFieldMixin):
    gl_iid = factory.Sequence(lambda seq: seq)
    title = factory.Faker('text', max_nb_chars=200)
    project = factory.SubFactory(ProjectFactory)
    time_estimate = factory.Faker('random_int')
    total_time_spent = factory.Faker('random_int')
    created_at = factory.Faker(
        'date_time_this_year',
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
    state = ISSUE_STATES.OPENED

    class Meta:
        model = Issue