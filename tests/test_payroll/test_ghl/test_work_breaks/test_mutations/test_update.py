from datetime import timedelta

from django.utils import timezone
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.core.gitlab import GITLAB_DATE_FORMAT
from apps.development.models import TeamMember
from apps.payroll.models.work_break import WorkBreak, WorkBreakReason
from apps.users.models import User
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories import UserFactory


def test_query(user, ghl_client, ghl_raw):
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
        ghl_raw("update_work_break"),
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
    """
    Test work break not team lead.

    :param ghl_auth_mock_info:
    :param update_work_break_mutation:
    """
    work_break = WorkBreakFactory.create(comment="django")

    update_variables = {
        "id": work_break.pk,
        "user": ghl_auth_mock_info.context.user.id,
        "from_date": timezone.now(),
        "to_date": timezone.now(),
        "reason": WorkBreakReason.DAYOFF,
        "comment": "test comment",
    }

    response = update_work_break_mutation(
        root=None,
        info=ghl_auth_mock_info,
        **update_variables,
    )
    assert isinstance(response, GraphQLPermissionDenied)

    work_break.refresh_from_db()

    assert work_break.comment == "django"


def test_update_work_break_another_user(
    ghl_auth_mock_info,
    update_work_break_mutation,
):
    """
    Test update work break another user.

    :param ghl_auth_mock_info:
    :param update_work_break_mutation:
    """
    team = TeamFactory.create()

    TeamMemberFactory.create(
        team=team,
        user=ghl_auth_mock_info.context.user,
        roles=TeamMember.roles.DEVELOPER,
    )

    user2 = UserFactory.create()
    TeamMemberFactory.create(
        team=team,
        user=user2,
        roles=TeamMember.roles.DEVELOPER,
    )

    work_break = WorkBreakFactory.create(user=user2, comment="created")

    update_variables = {
        "id": work_break.pk,
        "user": ghl_auth_mock_info.context.user.id,
        "from_date": timezone.now(),
        "to_date": timezone.now(),
        "reason": WorkBreakReason.DAYOFF,
        "comment": "test comment",
    }

    response = update_work_break_mutation(
        root=None,
        info=ghl_auth_mock_info,
        **update_variables,
    )
    assert isinstance(response, GraphQLPermissionDenied)


def test_update_another_user_but_team_lead(
    ghl_auth_mock_info,
    update_work_break_mutation,
    team,
    make_team_developer,
    make_team_leader,
):
    """
    Test update another user but team lead.

    :param ghl_auth_mock_info:
    :param update_work_break_mutation:
    :param team:
    :param make_team_developer:
    :param make_team_leader:
    """
    another_user = UserFactory.create()
    make_team_leader(team, ghl_auth_mock_info.context.user)
    make_team_developer(team, another_user)

    work_break = WorkBreakFactory.create(user=another_user, comment="created")

    update_variables = {
        "id": work_break.pk,
        "user": another_user.pk,
        "from_date": timezone.now().date(),
        "to_date": timezone.now().date(),
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
    assert work_break.user == another_user


def test_change_work_break_user(
    ghl_auth_mock_info,
    update_work_break_mutation,
):
    """
    Test change work break user.

    :param ghl_auth_mock_info:
    :param update_work_break_mutation:
    """
    team = TeamFactory.create()
    user2 = UserFactory.create()
    user3 = UserFactory.create()

    TeamMemberFactory.create(
        team=team,
        user=ghl_auth_mock_info.context.user,
        roles=TeamMember.roles.LEADER,
    )
    TeamMemberFactory.create(
        team=team,
        user=user2,
        roles=TeamMember.roles.DEVELOPER,
    )

    work_break = WorkBreakFactory.create(user=user2, comment="created")

    update_variables = {
        "id": work_break.pk,
        "user": user3.id,
        "from_date": timezone.now().date(),
        "to_date": timezone.now().date(),
        "reason": WorkBreakReason.DAYOFF,
        "comment": "updated",
        "paid_days": 7,
    }

    update_work_break_mutation(
        root=None,
        info=ghl_auth_mock_info,
        **update_variables,
    )

    work_break.refresh_from_db()

    assert WorkBreak.objects.count() == 1
    assert work_break.comment == "updated"
    assert work_break.user == user3
    assert work_break.paid_days == update_variables["paid_days"]


def _date_strftime(date):
    """
    Date strftime.

    :param date:
    """
    return date.strftime(GITLAB_DATE_FORMAT)
