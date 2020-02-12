import factory

from apps.development.models import Ticket
from apps.development.models.ticket import STATE_CREATED
from tests.test_development.factories.project_group_milestone import (
    ProjectGroupMilestoneFactory,
)


class TicketFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text", max_nb_chars=200)
    url = factory.Sequence(lambda seq: f"https://team-projector-{seq}.com")
    milestone = factory.SubFactory(ProjectGroupMilestoneFactory)
    state = STATE_CREATED

    class Meta:
        model = Ticket
