# -*- coding: utf-8 -*-

from datetime import timedelta

from django.utils import timezone
from pytest import raises

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.models import TeamMember
from apps.payroll.models.work_break import WorkBreak, WorkBreakReason
from apps.users.models import User
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories import UserFactory

GHL_QUERY_UPDATE_WORK_BREAK = """
mutation ($user: Int!, $id: ID!, $fromDate: DateTime!, $toDate: DateTime!,
 $reason: String!, $comment: String!) {
  updateWorkBreak(user: $user, id: $id, fromDate: $fromDate, toDate: $toDate,
   reason: $reason, comment: $comment) {
    workBreak {
      user {
        id
        name
      }
      id
      comment
    }
  }
}
"""

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def test_query(user, ghl_client):
    """Test update raw query."""
    ghl_client.set_user(user)

    team = TeamFactory.create()
    TeamMemberFactory.create(
        team=team,
        user=user,
        roles=TeamMember.roles.LEADER,
    )

    user.roles = User.roles.TEAM_LEADER
    user.save()

    work_break = WorkBreakFactory.create(user=user, comment="created")

    update_variables = {
        "id": work_break.pk,
        "user": user.id,
        "fromDate": _date_strftime(timezone.now()),
        "toDate": _date_strftime(timezone.now() + timedelta(minutes=10)),
        "reason": WorkBreakReason.DAYOFF,
        "comment": "test comment",
    }

    response = ghl_client.execute(
        GHL_QUERY_UPDATE_WORK_BREAK,
        variable_values=update_variables,
    )

    dto = response["data"]["updateWorkBreak"]["workBreak"]
    assert dto["id"] == str(work_break.pk)
    assert dto["user"]["id"] == str(update_variables["user"])
    assert dto["comment"] == update_variables["comment"]


def test_work_break_not_team_lead(
    ghl_auth_mock_info,
    update_work_break_mutation,
):
    work_break = WorkBreakFactory.create(comment="django")

    update_variables = {
        "id": work_break.pk,
        "user": ghl_auth_mock_info.context.user.id,
        "from_date": timezone.now(),
        "to_date": timezone.now(),
        "reason": WorkBreakReason.DAYOFF,
        "comment": "test comment",
    }

    with raises(GraphQLPermissionDenied):
        update_work_break_mutation(
            root=None,
            info=ghl_auth_mock_info,
            **update_variables,
        )
    work_break.refresh_from_db()

    assert work_break.comment == "django"


def test_update_work_break_another_user(
    ghl_auth_mock_info,
    update_work_break_mutation,
):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        team=team,
        user=ghl_auth_mock_info.context.user,
        roles=TeamMember.roles.DEVELOPER,
    )

    user_2 = UserFactory.create()
    TeamMemberFactory.create(
        team=team,
        user=user_2,
        roles=TeamMember.roles.DEVELOPER,
    )

    work_break = WorkBreakFactory.create(user=user_2, comment="created")

    update_variables = {
        "id": work_break.pk,
        "user": ghl_auth_mock_info.context.user.id,
        "from_date": timezone.now(),
        "to_date": timezone.now(),
        "reason": WorkBreakReason.DAYOFF,
        "comment": "test comment",
    }

    with raises(GraphQLPermissionDenied):
        update_work_break_mutation(
            root=None,
            info=ghl_auth_mock_info,
            **update_variables,
        )


def test_update_work_break_another_user_but_team_lead(
    ghl_auth_mock_info,
    update_work_break_mutation,
):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        team=team,
        user=ghl_auth_mock_info.context.user,
        roles=TeamMember.roles.LEADER,
    )

    user_2 = UserFactory.create()
    TeamMemberFactory.create(
        team=team,
        user=user_2,
        roles=TeamMember.roles.DEVELOPER,
    )

    work_break = WorkBreakFactory.create(user=user_2, comment="created")

    update_variables = {
        "id": work_break.pk,
        "user": user_2.id,
        "from_date": timezone.now(),
        "to_date": timezone.now(),
        "reason": WorkBreakReason.DAYOFF,
        "comment": "updated",
    }

    update_work_break_mutation(
        root=None,
        info=ghl_auth_mock_info,
        **update_variables,
    )

    work_break.refresh_from_db()

    assert WorkBreak.objects.count() == 1
    assert work_break.comment == "updated"
    assert work_break.user == user_2


def test_change_work_break_user(ghl_auth_mock_info, update_work_break_mutation):
    team = TeamFactory.create()
    user_2 = UserFactory.create()
    user_3 = UserFactory.create()

    TeamMemberFactory.create(
        team=team,
        user=ghl_auth_mock_info.context.user,
        roles=TeamMember.roles.LEADER,
    )
    TeamMemberFactory.create(
        team=team,
        user=user_2,
        roles=TeamMember.roles.DEVELOPER,
    )

    work_break = WorkBreakFactory.create(user=user_2, comment="created")

    update_variables = {
        "id": work_break.pk,
        "user": user_3.id,
        "from_date": timezone.now(),
        "to_date": timezone.now(),
        "reason": WorkBreakReason.DAYOFF,
        "comment": "updated",
    }

    update_work_break_mutation(
        root=None,
        info=ghl_auth_mock_info,
        **update_variables,
    )

    work_break.refresh_from_db()

    assert WorkBreak.objects.count() == 1
    assert work_break.comment == "updated"
    assert work_break.user == user_3


def _date_strftime(date):
    return date.strftime(DATE_TIME_FORMAT)
