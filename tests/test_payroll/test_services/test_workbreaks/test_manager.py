# -*- coding: utf-8 -*-

from apps.payroll.models.mixins.approved import ApprovedState
from apps.payroll.services import work_break as work_break_service
from tests.test_payroll.factories import WorkBreakFactory


def test_approve_by_teamlead(team_leader, team_developer):
    """
    Test approve by teamlead.

    :param team_leader:
    :param team_developer:
    """
    work_break = WorkBreakFactory.create(user=team_developer)

    work_break_service.Manager(work_break).approve(approved_by=team_leader)

    work_break.refresh_from_db()

    assert work_break.approve_state == ApprovedState.APPROVED
    assert work_break.approved_by == team_leader


def test_decline_by_teamlead(team_leader, team_developer):
    """
    Test decline by teamlead.

    :param team_leader:
    :param team_developer:
    """
    work_break = WorkBreakFactory.create(user=team_developer)

    work_break_service.Manager(work_break).decline(
        approved_by=team_leader, decline_reason="reason",
    )

    work_break.refresh_from_db()

    assert work_break.approve_state == ApprovedState.DECLINED
    assert work_break.approved_by == team_leader
    assert work_break.decline_reason == "reason"
