from django.db import connection
from django.test import override_settings

from tests.test_development.factories import IssueFactory


@override_settings(DEBUG=True)
def test_select_related_user(admin_user, gql_client_authenticated):
    IssueFactory.create(user=admin_user)
    query1 = '''
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

    query2 = '''
            {
              allIssues {
                edges {
                  node {
                    id
                    user {
                      id
                    }
                  }
                }
              }
            }
            '''

    count_before = len(connection.queries)
    gql_client_authenticated.execute(query1)
    for_request = len(connection.queries) - count_before

    gql_client_authenticated.execute(query2)
    assert len(connection.queries) == count_before + 2 * for_request
