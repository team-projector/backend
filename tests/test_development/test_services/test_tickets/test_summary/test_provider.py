from apps.development.models import Ticket
from apps.development.models.ticket import STATE_CREATED, STATE_PLANNING
from apps.development.services.ticket.summary import TicketsSummaryProvider
from tests.test_development.factories import (
    ProjectGroupMilestoneFactory,
    TicketFactory,
)


def test_all_fields(db):
    summary = TicketsSummaryProvider(Ticket.objects.all()).get_data()
    assert summary == {"accepting_count": 0,
                       "count": 0,
                       "created_count": 0,
                       "doing_count": 0,
                       "done_count": 0,
                       "planning_count": 0,
                       "testing_count": 0}


def test_selected_fields(db):
    summary = TicketsSummaryProvider(
        Ticket.objects.all(),
        fields=("count", "doing_count"),
    ).get_data()
    assert summary == {"count": 0,
                       "doing_count": 0}


def test_prefiltered_qs(db):
    milestone = ProjectGroupMilestoneFactory()
    TicketFactory(state=STATE_PLANNING, milestone=milestone)
    TicketFactory(state=STATE_PLANNING)
    TicketFactory(state=STATE_CREATED, milestone=milestone)
    TicketFactory(state=STATE_CREATED)

    summary = TicketsSummaryProvider(
        Ticket.objects.filter(milestone=milestone),
        fields=("count", "planning_count", "created_count"),
    ).get_data()
    assert summary == {"count": 2,
                       "planning_count": 1,
                       "created_count": 1}
