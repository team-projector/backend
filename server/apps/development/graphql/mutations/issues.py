import graphene
from rest_framework.generics import get_object_or_404

from apps.development.graphql.types import IssueType
from apps.development.models import Issue
from apps.development.tasks import sync_project_issue


class SyncIssueMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    issue = graphene.Field(IssueType)

    def mutate(self, info, id):
        issue = get_object_or_404(
            Issue.objects.allowed_for_user(info.context.user),
            pk=id
        )

        sync_project_issue.delay(
            issue.project.gl_id,
            issue.gl_iid
        )

        return SyncIssueMutation(issue=issue)
