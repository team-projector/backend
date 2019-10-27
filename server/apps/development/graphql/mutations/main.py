# -*- coding: utf-8 -*-

from apps.development.graphql.mutations.issues import (
    AddSpendIssueMutation,
    SyncIssueMutation,
    UpdateIssueMutation,
)
from apps.development.graphql.mutations.milestones import SyncMilestoneMutation
from apps.development.graphql.mutations.ticket import (
    CreateTicketMutation,
    UpdateTicketMutation,
)


class IssuesMutations:
    """Class representing list of available fields for issues mutations."""

    add_spend_time_issue = AddSpendIssueMutation.Field()
    sync_issue = SyncIssueMutation.Field()
    update_issue = UpdateIssueMutation.Field()


class TicketsMutations:
    """Class representing list of available fields for tickets mutations."""

    create_ticket = CreateTicketMutation.Field()
    update_ticket = UpdateTicketMutation.Field()


class MilestonesMutations:
    """Class representing list of available fields for milestones mutations."""

    sync_milestone = SyncMilestoneMutation.Field()
