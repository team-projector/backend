import graphene


class WorkItemTeamMetricsType(graphene.ObjectType):
    count = graphene.Int()
    opened_count = graphene.Int()
    opened_estimated = graphene.Int()


class IssueTeamMetricsType(WorkItemTeamMetricsType):
    pass


class MergeRequestTeamMetricsType(WorkItemTeamMetricsType):
    pass
