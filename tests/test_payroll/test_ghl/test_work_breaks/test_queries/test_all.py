from apps.payroll.models import WorkBreak
from tests.test_payroll.factories import WorkBreakFactory

GHL_QUERY_ALL_WORK_BREAKS = """
query ($team: ID, $user: ID, $offset: Int, $first: Int) {
  breaks: allWorkBreaks(team: $team, user: $user, offset: $offset,
   first: $first) {
    count
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
"""


def test_query(user, ghl_client):
    """Test create raw query."""
    ghl_client.set_user(user)

    work_break = WorkBreakFactory.create(user=user)

    response = ghl_client.execute(GHL_QUERY_ALL_WORK_BREAKS)

    assert response["data"]["breaks"]["count"] == 1

    node_dto = response["data"]["breaks"]["edges"][0]

    assert node_dto["node"]["id"] == str(work_break.pk)
    assert node_dto["node"]["user"]["id"] == str(user.id)


def test_not_team_lead(ghl_auth_mock_info, all_work_breaks_query):
    """
    Test not team lead.

    :param ghl_auth_mock_info:
    :param all_work_breaks_query:
    """
    WorkBreakFactory.create_batch(3)

    response = all_work_breaks_query(root=None, info=ghl_auth_mock_info)

    assert WorkBreak.objects.count() == 3
    assert not response.length
