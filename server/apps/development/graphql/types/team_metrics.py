import graphene


class WorkItemMetricsType(graphene.ObjectType):
    count = graphene.Int()
    opened_count = graphene.Int()


class TeamIssueMetricsType(WorkItemMetricsType):
    pass


class TeamMergeRequestMetricsType(WorkItemMetricsType):
    pass


class TeamMetricsType(graphene.ObjectType):
    problems_count = graphene.Int()
    issues = graphene.Field(TeamIssueMetricsType)
    merge_requests = graphene.Field(TeamMergeRequestMetricsType)
