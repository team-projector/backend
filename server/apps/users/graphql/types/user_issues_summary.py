import graphene


class UserIssuesSummaryType(graphene.ObjectType):
    """User issues summary type."""

    assigned_count = graphene.Int()
    created_count = graphene.Int()
    participation_count = graphene.Int()
