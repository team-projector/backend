import factory

from apps.development.models import Ticket
from tests.test_development.factories.project_group_milestone import (
    ProjectGroupMilestoneFactory,
)


class TicketFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('text', max_nb_chars=200)
    url = factory.Sequence(lambda s: f'https://team-projector-{s}.com')
    milestone = factory.SubFactory(ProjectGroupMilestoneFactory)

    class Meta:
        model = Ticket
