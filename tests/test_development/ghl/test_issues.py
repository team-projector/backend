from apps.development.graphql.types import IssueType, IssuesProjectSummary
from apps.development.graphql.mutations.issues import UpdateIssueMutation
from apps.development.models.issue import Issue
from tests.test_development.factories import (
    IssueFactory,
    ProjectGroupMilestoneFactory,
    TicketFactory,
    LabelFactory,
)
from tests.test_development.factories_gitlab import AttrDict
from tests.test_users.factories.user import UserFactory


def test_issue(user, client):
    issue = IssueFactory.create(user=user)
    IssueFactory.create_batch(3)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    node = IssueType().get_node(info, issue.id)

    assert node == issue


def test_all_issues(user, client):
    IssueFactory.create_batch(5, user=user)
    IssueFactory.create_batch(3)

    client.user = user
    info = AttrDict({
        'context': client,
        'field_asts': [{}],
        'fragments': {},
    })

    issues = IssueType().get_queryset(Issue.objects.all(), info)

    assert issues.count() == 5


def test_update_issue_ticket(user, client):
    issue = IssueFactory.create(user=user)
    ticket = TicketFactory.create(
        milestone=ProjectGroupMilestoneFactory.create())

    assert issue.ticket is None

    client.user = user
    info = AttrDict({'context': client})

    issue_mutated = UpdateIssueMutation.do_mutate(
        None, info, id=issue.id, ticket=ticket.id
    ).issue

    assert issue_mutated.ticket == ticket


def test_resolve_project(user):
    issue = IssueFactory.create(user=user)

    project = IssuesProjectSummary.resolve_project(issue, None)

    assert project == issue.project
