import factory
import pytz
from django.contrib.contenttypes.models import ContentType

from apps.development.models import (Feature, Issue, Label, Milestone, Note, Project, ProjectGroup, Team, TeamMember)
from apps.development.models.issue import STATE_OPENED


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
    content_type = factory.LazyAttribute(lambda o: ContentType.objects.get_for_model(o.owner))

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
    created_at = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    state = STATE_OPENED

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


class FeatureFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('text', max_nb_chars=200)
    budget = factory.Faker('random_int')
    milestone = factory.SubFactory(ProjectGroupMilestoneFactory)

    class Meta:
        model = Feature


def gl_user_factory() -> dict:
    """/user"""
    return {
        'id': 1,
        'name': 'User Test',
        'username': 'test_user',
        'state': 'active',
    }


def gl_project_factory(project_id: int) -> dict:
    """/projects/<project_id>"""
    return {
        'id': project_id,
        'description': 'Project Test',
        'name': 'Project Test',
    }


def gl_project_issues_factory(project_id: int, issue_id: int) -> dict:
    """/projects/<project_id>/issues"""
    return {
        'id': 1,
        'iid': issue_id,
        'project_id': project_id,
    }


def gl_issue_add_spent_time_factory() -> dict:
    """projects/<project_id>/issues/<issue_id>/add_spent_time"""
    return {
        'time_estimate': 60,
        'total_time_spent': 60,
        'human_time_estimate': '1m',
        'human_total_time_spent': '1m'
    }
