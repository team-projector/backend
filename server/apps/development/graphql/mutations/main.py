from .issues import AddSpendIssueMutation, SyncIssueMutation
from .milestones import SyncMilestoneMutation


class IssuesMutations:
    add_spend_time_issue = AddSpendIssueMutation.Field()
    sync_issue = SyncIssueMutation.Field()


class MilestonesMutations:
    sync_milestone = SyncMilestoneMutation.Field()
