import factory

from apps.development.models import Ticket
from apps.development.models.ticket import TicketState
from tests.test_development.factories.project_group_milestone import (
    ProjectGroupMilestoneFactory,
)


class TicketFactory(factory.django.DjangoModelFactory):
    """Ticket factory."""

    class Meta:
        model = Ticket

    title = factory.Faker("sentence")
    url = factory.Sequence(
        lambda seq: "https://team-projector-{0}.com".format(seq),
    )
    milestone = factory.SubFactory(ProjectGroupMilestoneFactory)
    state = TicketState.CREATED
