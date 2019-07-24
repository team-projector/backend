from apps.development.graphql.types.issue import IssueType
from apps.development.models import Issue
from tests.test_development.factories_gitlab import AttrDict
from tests.test_development.factories import IssueFactory


def test_list(user):
    IssueFactory.create_batch(5, user=user)

    issue_type = IssueType()

    info = AttrDict({
        'context': AttrDict({
            'user': user
        }),
        'field_asts': [{}],
        'fragments': {},

    })

    qs = issue_type.get_queryset(Issue.objects.all(), info)

    assert qs.count() == 5


def test_retrieve(user):
    issue = IssueFactory.create(user=user)

    issue_type = IssueType()

    info = AttrDict({
        'context': AttrDict({
            'user': user
        })
    })

    instance = issue_type.get_node(info, issue.id)

    assert instance == issue


def test_retrieve_not_found(user):
    issue = IssueFactory.create(user=user)

    issue_type = IssueType()

    info = AttrDict({
        'context': AttrDict({
            'user': user
        })
    })

    assert issue_type.get_node(info, issue.id + 1) is None
