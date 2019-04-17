import factory
import pytz
from django.contrib.contenttypes.models import ContentType

from apps.development.models import Issue, Label, Note, Project, ProjectGroup, STATE_OPENED, Team, TeamMember, \
    Milestone, Epic


class GitlabFieldMixin(factory.django.DjangoModelFactory):
    gl_id = factory.Sequence(lambda i: i)
    gl_url = factory.Sequence(lambda s: f'https://team-projector-{s}.com')


class ProjectGroupFactory(GitlabFieldMixin):
    title = factory.Faker('text', max_nb_chars=200)

    class Meta:
        model = ProjectGroup


class LabelFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('text', max_nb_chars=200)
    address = factory.Faker('address')

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
    title = factory.Faker('text', max_nb_chars=200)
    project = factory.SubFactory(ProjectFactory)
    time_estimate = factory.Faker('random_int')
    total_time_spent = factory.Faker('random_int')
    created_at = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    state = STATE_OPENED

    milestone = factory.SubFactory(ProjectGroupMilestoneFactory)

    class Meta:
        model = Issue


class IssueNoteFactory(factory.django.DjangoModelFactory):
    gl_id = factory.Sequence(lambda i: i)
    created_at = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
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


class EpicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Epic
