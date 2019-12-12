from datetime import datetime
from pytest import raises
from rest_framework.exceptions import PermissionDenied

from apps.development.models import TeamMember
from apps.payroll.models import WorkBreak
from apps.payroll.graphql.mutations.work_breaks import (
    CreateWorkBreakMutation, DeleteWorkBreakMutation, UpdateWorkBreakMutation
)
from apps.payroll.graphql.queries.work_breaks import WorkBreakType
from apps.payroll.models.work_break import WORK_BREAK_REASONS
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_development.factories_gitlab import AttrDict
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories.user import UserFactory


def test_work_break(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.LEADER)
    work_break_1 = WorkBreakFactory.create(user=user)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)
    work_break_2 = WorkBreakFactory.create(user=user_2)

    client.user = user
    info = AttrDict({'context': client})

    assert WorkBreakType.get_node(info, work_break_1.id) == work_break_1
    assert WorkBreakType.get_node(info, work_break_2.id) == work_break_2


def test_work_break_not_team_lead(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.LEADER)
    work_break_1 = WorkBreakFactory.create(user=user)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)
    work_break_2 = WorkBreakFactory.create(user=user_2)

    client.user = user_2
    info = AttrDict({'context': client})

    assert WorkBreakType.get_node(info, work_break_1.id) is None
    assert WorkBreakType.get_node(info, work_break_2.id) == work_break_2


def test_work_breaks(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.LEADER)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)
    WorkBreakFactory.create_batch(5, user=user_2)

    client.user = user_2
    info = AttrDict({'context': client})

    work_breaks = WorkBreakType.get_queryset(WorkBreak.objects.all(), info)

    assert work_breaks.count() == 5


def test_create_work_break(user, client):
    client.user = user
    info = AttrDict({'context': client})

    work_break_created = CreateWorkBreakMutation.mutate(
        None,
        info,
        comment='created',
        from_date=str(datetime.now()),
        reason=WORK_BREAK_REASONS.DAYOFF,
        to_date=str(datetime.now()),
        user=user.id
    ).work_break

    assert WorkBreak.objects.count() == 1
    assert work_break_created.comment == 'created'
    assert work_break_created.from_date is not None
    assert work_break_created.reason == WORK_BREAK_REASONS.DAYOFF
    assert work_break_created.to_date is not None
    assert work_break_created.user == user


def test_update_work_break(user, client):
    work_break = WorkBreakFactory.create(user=user, comment='created')

    client.user = user
    info = AttrDict({'context': client})

    work_break_mutated = UpdateWorkBreakMutation.mutate(
        None,
        info,
        id=work_break.id,
        comment='updated',
        from_date=str(datetime.now()),
        reason=WORK_BREAK_REASONS.VACATION,
        to_date=str(datetime.now()),
        user=user.id
    ).work_break

    work_break.refresh_from_db()
    assert WorkBreak.objects.count() == 1
    assert work_break.comment == 'updated'
    assert work_break.user == user


def test_update_work_break_another_user(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.DEVELOPER)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)

    work_break = WorkBreakFactory.create(user=user_2, comment='created')

    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        UpdateWorkBreakMutation.mutate(
            None,
            info,
            id=work_break.id,
            comment='updated',
            from_date=str(datetime.now()),
            reason=WORK_BREAK_REASONS.VACATION,
            to_date=str(datetime.now())
        ).work_break


def test_update_work_break_another_user_but_teamlead(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.LEADER)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)

    work_break = WorkBreakFactory.create(user=user_2, comment='created')

    client.user = user
    info = AttrDict({'context': client})

    work_break_mutated = UpdateWorkBreakMutation.mutate(
        None,
        info,
        id=work_break.id,
        comment='updated',
        from_date=str(datetime.now()),
        reason=WORK_BREAK_REASONS.VACATION,
        to_date=str(datetime.now())
    ).work_break

    work_break.refresh_from_db()
    assert WorkBreak.objects.count() == 1
    assert work_break.comment == 'updated'
    assert work_break.user == user_2


def test_delete_work_break(user, client):
    work_break = WorkBreakFactory.create(user=user, comment='created')

    client.user = user
    info = AttrDict({'context': client})

    assert WorkBreak.objects.count() == 1

    DeleteWorkBreakMutation.mutate(
        None,
        info,
        id=work_break.id,
        user=user.id
    )

    assert WorkBreak.objects.count() == 0
