from apps.development.models import Ticket
from apps.development.models.ticket import TicketState
from apps.development.services.ticket.summary import TicketsSummaryProvider
from tests.test_development.factories import (
    ProjectGroupMilestoneFactory,
    TicketFactory,
)

KEY_COUNT = "count"


def test_all_fields(db):
    """
    Test all fields.

    :param db:
    """
    summary = TicketsSummaryProvider(Ticket.objects.all()).get_data()
    assert summary == {
        "accepting_count": 0,
        KEY_COUNT: 0,
        "created_count": 0,
        "doing_count": 0,
        "done_count": 0,
        "planning_count": 0,
        "testing_count": 0,
    }


def test_selected_fields(db):
    """
    Test selected fields.

    :param db:
    """
    summary = TicketsSummaryProvider(
        Ticket.objects.all(),
        fields=("count", "doing_count"),
    ).get_data()

    assert summary == {KEY_COUNT: 0, "doing_count": 0}


def test_prefiltered_qs(db):
    """
    Test prefiltered qs.

    :param db:
    """
    milestone = ProjectGroupMilestoneFactory.create()
    TicketFactory.create(state=TicketState.PLANNING, milestone=milestone)
    TicketFactory.create(state=TicketState.PLANNING)
    TicketFactory.create(state=TicketState.CREATED, milestone=milestone)
    TicketFactory.create(state=TicketState.CREATED)

    summary = TicketsSummaryProvider(
        Ticket.objects.filter(milestone=milestone),
        fields=("count", "planning_count", "created_count"),
    ).get_data()

    assert summary == {KEY_COUNT: 2, "planning_count": 1, "created_count": 1}
