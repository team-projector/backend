# -*- coding: utf-8 -*-

from pytest import raises

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.models import TeamMember
from apps.payroll.models.mixins.approved import APPROVED_STATES
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
    user_1 = UserFactory.create()

    TeamMemberFactory.create(
        team=team,
        user=user,
        roles=TeamMember.roles.LEADER
    )
    TeamMemberFactory.create(
        team=team,
        user=user_1,
        roles=TeamMember.roles.DEVELOPER
    )
    work_break = WorkBreakFactory.create(user=user_1)

    response = ghl_client.execute(
        GHL_QUERY_APPROVE_WORK_BREAK,
        variable_values={"id": work_break.pk},
    )

    work_break.refresh_from_db()

    assert response["data"]["approveWorkBreak"]["workBreak"]["id"] == (
        str(work_break.id)
    )
    assert work_break.approved_by == user
    assert work_break.approve_state == APPROVED_STATES.APPROVED


def test_not_team_lead(ghl_auth_mock_info, approve_work_break_mutation):
    work_break = WorkBreakFactory.create()

    with raises(GraphQLPermissionDenied):
        approve_work_break_mutation(
            root=None,
            info=ghl_auth_mock_info,
            id=work_break.pk,
        )

    work_break.refresh_from_db()

    assert not work_break.approved_by
    assert work_break.approve_state == APPROVED_STATES.CREATED


def test_owner(ghl_auth_mock_info, approve_work_break_mutation):
    work_break = WorkBreakFactory.create(user=ghl_auth_mock_info.context.user)

    with raises(GraphQLPermissionDenied):
        approve_work_break_mutation(
            root=None,
            info=ghl_auth_mock_info,
            id=work_break.pk,
        )

    work_break.refresh_from_db()

    assert not work_break.approved_by
    assert work_break.approve_state == APPROVED_STATES.CREATED