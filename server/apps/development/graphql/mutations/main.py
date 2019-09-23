from .issues import (
    AddSpendIssueMutation, SyncIssueMutation, UpdateIssueMutation,
)
from .milestones import SyncMilestoneMutation
from .ticket import CreateTicketMutation, UpdateTicketMutation


class IssuesMutations:
    add_spend_time_issue = AddSpendIssueMutation.Field()
    sync_issue = SyncIssueMutation.Field()
    update_issue = UpdateIssueMutation.Field()


class TicketsMutations:
    create_ticket = CreateTicketMutation.Field()
    update_ticket = UpdateTicketMutation.Field()


class MilestonesMutations:
    sync_milestone = SyncMilestoneMutation.Field()
