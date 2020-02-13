import factory

from apps.development.models import Ticket
from apps.development.models.ticket import TicketState
from tests.test_development.factories.project_group_milestone import (
    ProjectGroupMilestoneFactory,
)


class TicketFactory(factory.django.DjangoModelFactory):
    title = factory.Faker("text", max_nb_chars=200)
    url = factory.Sequence(
        lambda seq: "https://team-projector-{0}.com".format(seq),
    )
    milestone = factory.SubFactory(ProjectGroupMilestoneFactory)
    state = TicketState.CREATED

    class Meta:
        model = Ticket
