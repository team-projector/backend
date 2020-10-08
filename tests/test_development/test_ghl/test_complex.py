from tests.test_development.factories import IssueFactory


def test_connection_anonymous(user, gql_client_anonymous):
    """
    Test connection anonymous.

    :param user:
    :param gql_client_anonymous:
    """
    IssueFactory.create_batch(5, user=user)

    query = """
    {
      allIssues(state: "opened") {
        edges {
          node {
            id
          }
        }
      }
    }"""

    response = gql_client_anonymous.execute(query)["data"]
    assert response["allIssues"] is None


def test_connection_authenticated(admin_user, gql_client_authenticated):
    """
    Test connection authenticated.

    :param admin_user:
    :param gql_client_authenticated:
    """
    IssueFactory.create_batch(5, user=admin_user)
    IssueFactory.create_batch(3)

    query = """
    fragment issueFields on Issue {
      title
    }

    {
      allIssues(first:5, last:1, state: "OPENED") {
        count
        edges {
          node {
            id
            ...issueFields
          }
        }
      }
    }"""

    response = gql_client_authenticated.execute(query)["data"]
    assert response["allIssues"]["count"] == 5


def test_relay_node(admin_user, gql_client_authenticated):
    """
    Test relay node.

    :param admin_user:
    :param gql_client_authenticated:
    """
    IssueFactory.create(id=1, user=admin_user)
    IssueFactory.create_batch(3)

    query = """
    {
      issue(id: 1) {
        id
      }
    }"""

    response = gql_client_authenticated.execute(query)["data"]
    assert int(response["issue"]["id"]) == 1
