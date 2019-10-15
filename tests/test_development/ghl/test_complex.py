from tests.test_development.factories import IssueFactory


def test_connection(admin_user, gql_client_authenticated):
    IssueFactory.create_batch(5, user=admin_user)
    IssueFactory.create_batch(3)

    query = '''{
      allIssues(first:5, last:1, state: "opened") {
        count
        edges {
          node {
            id
          }
        }
      }
    }'''

    data = gql_client_authenticated.execute(query)['data']

    assert data['allIssues']['count'] == 5


def test_relay_node(admin_user, gql_client_authenticated):
    IssueFactory.create(id=1, user=admin_user)
    IssueFactory.create_batch(3)

    query = '''{
      issue(id: 1) {
        id
      }
    }'''

    data = gql_client_authenticated.execute(query)['data']

    assert int(data['issue']['id']) == 1
