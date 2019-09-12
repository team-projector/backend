import factory
import pytz
from django.contrib.contenttypes.models import ContentType

from apps.development.models import (
    Ticket, Issue, Label, Milestone, Note, Project, ProjectGroup, Team,
    TeamMember, MergeRequest
)
from apps.development.models.issue import STATE_OPENED
from tests.test_users.factories import UserFactory


class GitlabFieldMixin(factory.django.DjangoModelFactory):
    gl_id = factory.Sequence(lambda i: i)
    gl_url = factory.Sequence(lambda s: f'https://team-projector-{s}.com')


class ProjectGroupFactory(GitlabFieldMixin):
    title = factory.Faker('text', max_nb_chars=200)

    class Meta:
        model = ProjectGroup


class LabelFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('text', max_nb_chars=200)
    color = factory.Faker('text', max_nb_chars=10)

    class Meta:
        model = Label


class ProjectFactory(GitlabFieldMixin):
    title = factory.Faker('text', max_nb_chars=200)

    class Meta:
        model = Project


class MilestoneFactory(GitlabFieldMixin):
    owner = factory.SubFactory(ProjectGroupFactory)
    object_id = factory.SelfAttribute('owner.id')
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.owner))

    class Meta:
        abstract = True
        exclude = ['content_object']


class ProjectGroupMilestoneFactory(MilestoneFactory):
    owner = factory.SubFactory(ProjectGroupFactory)

    class Meta:
        model = Milestone


class ProjectMilestoneFactory(MilestoneFactory):
    owner = factory.SubFactory(ProjectFactory)

    class Meta:
        model = Milestone


class IssueFactory(GitlabFieldMixin):
    gl_iid = factory.Sequence(lambda i: i)
    title = factory.Faker('text', max_nb_chars=200)
    project = factory.SubFactory(ProjectFactory)
    time_estimate = factory.Faker('random_int')
    total_time_spent = factory.Faker('random_int')
    created_at = factory.Faker('date_time_this_year', before_now=True,
                               after_now=False, tzinfo=pytz.UTC)
    state = STATE_OPENED

    class Meta:
        model = Issue


class IssueNoteFactory(factory.django.DjangoModelFactory):
    gl_id = factory.Sequence(lambda i: i)
    created_at = factory.Faker('date_time_this_year', before_now=True,
                               after_now=False, tzinfo=pytz.UTC)
    content_object = factory.SubFactory(IssueFactory)
    data = {}

    class Meta:
        model = Note


class TeamFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('text', max_nb_chars=200)

    class Meta:
        model = Team


class TeamMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeamMember


class TicketFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('text', max_nb_chars=200)
    url = factory.Sequence(lambda s: f'https://team-projector-{s}.com')
    milestone = factory.SubFactory(ProjectGroupMilestoneFactory)

    class Meta:
        model = Ticket


class MergeRequestFactory(GitlabFieldMixin):
    state = STATE_OPENED
    title = factory.Faker('text', max_nb_chars=200)
    time_estimate = factory.Faker('random_int')
    milestone = factory.SubFactory(ProjectGroupMilestoneFactory)
    gl_iid = factory.Sequence(lambda i: i)
    author = factory.SubFactory(UserFactory)
    created_at = factory.Faker('date_time_this_year', before_now=True,
                               after_now=False, tzinfo=pytz.UTC)

    class Meta:
        model = MergeRequest
