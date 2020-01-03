from apps.development.models import TeamMember
from apps.payroll.models.mixins.approved import APPROVED_STATES
from apps.payroll.services import work_break as work_break_service
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories.user import UserFactory


def test_approve_by_teamlead(user):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.LEADER)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)

    work_break = WorkBreakFactory.create(user=user_2)

    work_break_service.Manager(work_break).approve(
        approved_by=user
    )

    work_break.refresh_from_db()

    assert work_break.approve_state == APPROVED_STATES.APPROVED
    assert work_break.approved_by == user


def test_decline_by_teamlead(user):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.LEADER)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)

    work_break = WorkBreakFactory.create(user=user_2)

    work_break_service.Manager(work_break).decline(
        approved_by=user,
        decline_reason="reason"
    )

    work_break.refresh_from_db()

    assert work_break.approve_state == APPROVED_STATES.DECLINED
    assert work_break.approved_by == user
    assert work_break.decline_reason == "reason"
