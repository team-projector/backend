from .issues import (
    AddSpendIssueMutation, SyncIssueMutation, UpdateIssueMutation
)
from .milestones import SyncMilestoneMutation


class IssuesMutations:
    add_spend_time_issue = AddSpendIssueMutation.Field()
    sync_issue = SyncIssueMutation.Field()
    update_issue = UpdateIssueMutation.Field()


class MilestonesMutations:
    sync_milestone = SyncMilestoneMutation.Field()
