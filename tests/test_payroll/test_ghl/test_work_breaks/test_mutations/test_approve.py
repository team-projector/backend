# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.models import TeamMember
from apps.payroll.models.mixins.approved import ApprovedState
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories import UserFactory

GHL_QUERY_APPROVE_WORK_BREAK = """
mutation ($id: ID!) {
  approveWorkBreak(id: $id) {
    workBreak {
      id
    }
  }
}
"""


def test_query(user, ghl_client):
    """Test create raw query."""
    ghl_client.set_user(user)

    team = TeamFactory.create()
    user1 = UserFactory.create()

    TeamMemberFactory.create(
        team=team, user=user, roles=TeamMember.roles.LEADER,
    )
    TeamMemberFactory.create(
        team=team, user=user1, roles=TeamMember.roles.DEVELOPER,
    )
    work_break = WorkBreakFactory.create(user=user1)

    response = ghl_client.execute(
        GHL_QUERY_APPROVE_WORK_BREAK, variable_values={"id": work_break.pk},
    )

    work_break.refresh_from_db()

    assert response["data"]["approveWorkBreak"]["workBreak"]["id"] == (
        str(work_break.id)
    )
    assert work_break.approved_by == user
    assert work_break.approve_state == ApprovedState.APPROVED


def test_not_team_lead(ghl_auth_mock_info, approve_work_break_mutation):
    work_break = WorkBreakFactory.create()

    with pytest.raises(GraphQLPermissionDenied):
        approve_work_break_mutation(
            root=None, info=ghl_auth_mock_info, id=work_break.pk,
        )

    work_break.refresh_from_db()

    assert not work_break.approved_by
    assert work_break.approve_state == ApprovedState.CREATED


def test_other_team_teamlead(  # noqa: WPS211
    user,
    ghl_auth_mock_info,
    team,
    make_team_developer,
    make_team_leader,
    approve_work_break_mutation,
):
    make_team_leader(team, user)

    another_team = TeamFactory.create()
    another_user = UserFactory.create()
    make_team_developer(another_team, another_user)

    work_break = WorkBreakFactory.create(user=another_user)

    with pytest.raises(GraphQLPermissionDenied):
        approve_work_break_mutation(
            root=None, info=ghl_auth_mock_info, id=work_break.id,
        )


def test_owner(ghl_auth_mock_info, approve_work_break_mutation):
    work_break = WorkBreakFactory.create(user=ghl_auth_mock_info.context.user)

    with pytest.raises(GraphQLPermissionDenied):
        approve_work_break_mutation(
            root=None, info=ghl_auth_mock_info, id=work_break.pk,
        )

    work_break.refresh_from_db()

    assert not work_break.approved_by
    assert work_break.approve_state == ApprovedState.CREATED
