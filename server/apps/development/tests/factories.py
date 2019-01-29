import factory
import pytz

from apps.development.models import Issue, Label, Project, ProjectGroup


class ProjectGroupFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('text', max_nb_chars=200)

    gl_id = factory.Faker('random_int', min=0, max=999)
    gl_url = factory.Faker('url')

    class Meta:
        model = ProjectGroup


class LabelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Label

    title = factory.Faker('text', max_nb_chars=200)
    address = factory.Faker('address')


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    title = factory.Faker('text', max_nb_chars=200)
    gl_id = factory.Faker('random_int', min=0, max=999)
    gl_url = factory.Faker('url')


class IssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Issue

    title = factory.Faker('text', max_nb_chars=200)
    project = factory.SubFactory(ProjectFactory)
    time_estimate = factory.Faker('random_int')
    total_time_spent = factory.Faker('random_int')
    state = factory.Faker('random_element', elements=['closed', 'opened'])
    created_at = factory.Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    gl_id = factory.Faker('random_int', min=0, max=999)
    gl_url = factory.Faker('url')
