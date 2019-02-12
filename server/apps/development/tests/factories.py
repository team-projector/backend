import factory
import pytz

from apps.development.models import Issue, Label, Note, Project, ProjectGroup, STATE_OPENED


class ProjectGroupFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('text', max_nb_chars=200)

    gl_id = factory.Faker('random_int', min=0, max=999)
    gl_url = factory.Faker('url')

    class Meta:
        model = ProjectGroup


class LabelFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('text', max_nb_chars=200)
    address = factory.Faker('address')

    class Meta:
        model = Label


class ProjectFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('text', max_nb_chars=200)
    gl_id = factory.Faker('random_int', min=0, max=999)
    gl_url = factory.Faker('url')

    class Meta:
        model = Project


class IssueFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('text', max_nb_chars=200)
    project = factory.SubFactory(ProjectFactory)
    time_estimate = factory.Faker('random_int')
    total_time_spent = factory.Faker('random_int')
    created_at = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    gl_id = factory.Faker('random_int', min=0, max=999)
    gl_url = factory.Faker('url')
    state = STATE_OPENED

    class Meta:
        model = Issue


class IssueNoteFactory(factory.django.DjangoModelFactory):
    gl_id = factory.Faker('random_int', min=0, max=9999)
    created_at = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    content_object = factory.SubFactory(IssueFactory)
    data = {}

    class Meta:
        model = Note
