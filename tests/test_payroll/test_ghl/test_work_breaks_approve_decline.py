from pytest import raises
from rest_framework.exceptions import PermissionDenied

from apps.development.models import TeamMember
from apps.payroll.graphql.mutations.work_breaks import (
    ApproveWorkBreakMutation, DeclineWorkBreakMutation
)
from apps.payroll.models.mixins.approved import APPROVED_STATES
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_development.factories_gitlab import AttrDict
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories.user import UserFactory


def test_approve_by_teamlead(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.LEADER)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)

    work_break = WorkBreakFactory.create(user=user_2)

    client.user = user
    info = AttrDict({'context': client})

    work_break_mutated = ApproveWorkBreakMutation.mutate(
        root=None,
        info=info,
        id=work_break.id
    ).work_break

    assert work_break_mutated.approve_state == APPROVED_STATES.APPROVED
    assert work_break_mutated.approved_by == user


def test_approve_by_other_team_teamlead(user, client):
    team_1 = TeamFactory.create()
    TeamMemberFactory.create(team=team_1,
                             user=user,
                             roles=TeamMember.roles.LEADER)

    team_2 = TeamFactory.create()
    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team_2,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)

    work_break = WorkBreakFactory.create(user=user_2)

    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        ApproveWorkBreakMutation.mutate(
            root=None,
            info=info,
            id=work_break.id
        )


def test_approve_by_current_user(user, client):
    work_break = WorkBreakFactory.create(user=user)

    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        ApproveWorkBreakMutation.mutate(
            root=None,
            info=info,
            id=work_break.id,
            decline_reason='reason'
        )


def test_decline_by_teamlead(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.LEADER)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)

    work_break = WorkBreakFactory.create(user=user_2)

    client.user = user
    info = AttrDict({'context': client})

    work_break_mutated = DeclineWorkBreakMutation.mutate(
        root=None,
        info=info,
        id=work_break.id,
        decline_reason='reason'
    ).work_break

    assert work_break_mutated.approve_state == APPROVED_STATES.DECLINED
    assert work_break_mutated.approved_by == user
    assert work_break_mutated.decline_reason == 'reason'


def test_decline_by_other_team_teamlead(user, client):
    team_1 = TeamFactory.create()
    TeamMemberFactory.create(team=team_1,
                             user=user,
                             roles=TeamMember.roles.LEADER)

    team_2 = TeamFactory.create()
    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team_2,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)

    work_break = WorkBreakFactory.create(user=user_2)

    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        DeclineWorkBreakMutation.mutate(
            root=None,
            info=info,
            id=work_break.id,
            decline_reason='reason'
        )


def test_decline_by_current_user(user, client):
    work_break = WorkBreakFactory.create(user=user)

    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        DeclineWorkBreakMutation.mutate(
            root=None,
            info=info,
            id=work_break.id,
            decline_reason='reason'
        )
