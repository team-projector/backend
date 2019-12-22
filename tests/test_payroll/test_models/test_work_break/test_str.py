from apps.payroll.models.work_break import WORK_BREAK_REASONS
from tests.test_payroll.factories import WorkBreakFactory


def test_str(user):
    work_break = WorkBreakFactory.create(
        reason=WORK_BREAK_REASONS.DAYOFF,
        user=user,
    )

    assert str(work_break) == '{0}: {1} ({2} - {3})'.format(
        user.login,
        WORK_BREAK_REASONS.DAYOFF,
        work_break.from_date,
        work_break.to_date,
    )
