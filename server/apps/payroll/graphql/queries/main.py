from apps.payroll.graphql.queries import (
    bonuses,
    penalties,
    salaries,
    spent_times,
    work_breaks,
)


class PayrollQueries(  # noqa: WPS215
    salaries.SalariesQueries,
    penalties.PenaltiesQueries,
    spent_times.TimeExpensesQueries,
    work_breaks.WorkBreaksQueries,
    bonuses.BonusesQueries,
):
    """Class representing list of all queries."""
