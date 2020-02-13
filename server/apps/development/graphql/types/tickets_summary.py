# -*- coding: utf-8 -*-

import graphene

from apps.development.models.ticket import TICKET_STATES


class _TicketsSummaryBase(graphene.ObjectType):
    count = graphene.Int()


TicketsSummaryType = type("TicketsSummaryType", (_TicketsSummaryBase,), {
    "{0}_count".format(state.lower()): graphene.Int()
    for state
    in TICKET_STATES.keys()
})
