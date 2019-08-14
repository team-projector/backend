import graphene
from django.utils.translation import gettext_lazy as _
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.core.graphql.mutations import BaseMutation
from apps.development.graphql.types import IssueType
from apps.development.models import Issue, Feature
from apps.development.services.gitlab.spent_time import add_spent_time
from apps.development.tasks import sync_project_issue


class AddSpendIssueMutation(BaseMutation):
    class Arguments:
        id = graphene.ID()
        seconds = graphene.Int(required=True)

    issue = graphene.Field(IssueType)

    @classmethod
    def do_mutate(cls, root, info, id, seconds):
        if not info.context.user.gl_token:
            raise ValidationError(_('MSG_PLEASE_PROVIDE_PERSONAL_GL_TOKEN'))

        if seconds < 1:
            raise ValidationError(_('MSG_SPEND_SHOULD_BE_GREATER_THAN_ONE'))

        issue = get_object_or_404(
            Issue.objects.allowed_for_user(info.context.user),
            pk=id
        )

        add_spent_time(
            info.context.user,
            issue,
            seconds
        )

        return AddSpendIssueMutation(issue=issue)


class SyncIssueMutation(BaseMutation):
    class Arguments:
        id = graphene.ID()

    issue = graphene.Field(IssueType)

    @classmethod
    def do_mutate(cls, root, info, id):
        issue = get_object_or_404(
            Issue.objects.allowed_for_user(info.context.user),
            pk=id
        )

        sync_project_issue.delay(
            issue.project.gl_id,
            issue.gl_iid
        )

        return SyncIssueMutation(issue=issue)


class UpdateIssueMutation(BaseMutation):
    class Arguments:
        id = graphene.ID()
        feature = graphene.Int()

    issue = graphene.Field(IssueType)

    @classmethod
    def do_mutate(cls, root, info, id, **kwargs):
        issue = get_object_or_404(
            Issue.objects.allowed_for_user(info.context.user),
            pk=id
        )

        if kwargs.get('feature'):
            feature = get_object_or_404(
                Feature.objects.all(),
                pk=kwargs.pop('feature')
            )
            issue.feature = feature

        issue.save()

        return UpdateIssueMutation(issue=issue)
