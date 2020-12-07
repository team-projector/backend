from apps.payroll.models import WorkBreak
from apps.payroll.services.work_break import filter_allowed_for_user
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories.user import UserFactory


def test_my_work_breaks(user):
    """
    Test my work breaks.

    :param user:
    """
    work_breaks = WorkBreakFactory.create_batch(size=3, user=user)

    WorkBreakFactory.create_batch(size=5, user=UserFactory.create())

    assert set(filter_allowed_for_user(WorkBreak.objects.all(), user)) == set(
        work_breaks,
    )


def test_my_work_breaks_and_as_leader(
    user,
    make_team_leader,
    team,
    team_developer,
):
    """
    Test my work breaks and as leader.

    :param user:
    :param make_team_leader:
    :param team:
    :param team_developer:
    """
    make_team_leader(team, user)

    work_breaks = {
        *WorkBreakFactory.create_batch(size=3, user=user),
        *WorkBreakFactory.create_batch(size=3, user=team_developer),
    }

    assert (
        set(filter_allowed_for_user(WorkBreak.objects.all(), user))
        == work_breaks
    )
