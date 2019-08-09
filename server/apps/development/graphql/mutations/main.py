from .issues import SyncIssueMutation
from .milestones import SyncMilestoneMutation


class IssuesMutations:
    sync_issue = SyncIssueMutation.Field()


class MilestonesMutations:
    sync_milestone = SyncMilestoneMutation.Field()
