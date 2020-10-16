from apps.development.graphql.mutations import (
    issues,
    merge_requests,
    milestones,
    tickets,
)


class DevelopmentMutations:
    """Class representing list of all mutations."""

    sync_milestone = milestones.SyncMilestoneMutation.Field()

    create_ticket = tickets.CreateTicketMutation.Field()
    delete_ticket = tickets.DeleteTicketMutation.Field()
    update_ticket = tickets.UpdateTicketMutation.Field()

    add_spend_time_issue = issues.AddSpentToIssueMutation.Field()
    sync_issue = issues.SyncIssueMutation.Field()
    update_issue = issues.UpdateIssueMutation.Field()

    sync_merge_request = merge_requests.SyncMergeRequestMutation.Field()
