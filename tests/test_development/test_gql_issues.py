from collections import Counter

from apps.development.graphql.mutations.issues import UpdateIssueMutation
from tests.test_development.factories import (
    TicketFactory, IssueFactory, ProjectGroupMilestoneFactory,
)
from tests.test_development.factories_gitlab import AttrDict


def test_all_issues(admin_user, gql_client_authenticated):
    issues = IssueFactory.create_batch(5, user=admin_user)
    IssueFactory.create_batch(3)

    query = '''
            {
              allIssues {
                edges {
                  node {
                    id
                  }
                }
              }
            }
            '''

    result = gql_client_authenticated.execute(query)

    actual = Counter([e['node']['id']
                      for e
                      in result['data']['allIssues']['edges']])

    assert actual == Counter([str(obj.id) for obj in issues])


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
