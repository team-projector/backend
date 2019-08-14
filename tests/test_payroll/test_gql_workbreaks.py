from apps.development.models import TeamMember
from apps.payroll.models import WorkBreak
from apps.payroll.graphql.queries.work_break import WorkBreakType
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_development.factories_gitlab import AttrDict
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories import UserFactory


def test_work_break(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.leader)
    work_break_1 = WorkBreakFactory.create(user=user)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.developer)
    work_break_2 = WorkBreakFactory.create(user=user_2)

    client.user = user
    info = AttrDict({'context': client})

    assert WorkBreakType.get_node(info, work_break_1.id) == work_break_1
    assert WorkBreakType.get_node(info, work_break_2.id) == work_break_2


def test_work_break_not_team_lead(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.leader)
    work_break_1 = WorkBreakFactory.create(user=user)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.developer)
    work_break_2 = WorkBreakFactory.create(user=user_2)

    client.user = user_2
    info = AttrDict({'context': client})

    assert WorkBreakType.get_node(info, work_break_1.id) is None
    assert WorkBreakType.get_node(info, work_break_2.id) == work_break_2


def test_work_breaks(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.leader)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.developer)
    WorkBreakFactory.create_batch(5, user=user_2)

    client.user = user_2
    info = AttrDict({'context': client})

    work_breaks = WorkBreakType.get_queryset(WorkBreak.objects.all(), info)

    assert work_breaks.count() == 5
