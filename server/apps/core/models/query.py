from constance import config
from django.db.models import Func


def _generate_trunc_week_template() -> str:
    """Generate template for TruncWeek expression."""
    expression = "%(expressions)s"  # noqa: WPS323
    days_passed = "(extract(ISODOW from {0}) - 1 - {1})".format(
        expression,
        config.FIRST_WEEK_DAY,
    )

    return """
    DATE(case
    when {days_passed} < 0 then
        {expression} - (({days_passed} + 7) * interval '1 day')
    when {days_passed} > 0 then
        {expression} - ({days_passed} * interval '1 day')
    else
        {expression}
    end)
    """.format(
        expression=expression,
        days_passed=days_passed,
    )


class TruncWeek(Func):
    """Trancate week for database."""

    def __init__(self, *args, **kwargs):
        """Initialize truncate week expression."""
        self.template = _generate_trunc_week_template()
        super().__init__(*args, **kwargs)
