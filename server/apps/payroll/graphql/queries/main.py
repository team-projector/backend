# -*- coding: utf-8 -*-

from apps.payroll.graphql.queries import salaries, spent_times, work_breaks


class PayrollQueries(
    salaries.SalariesQueries,
    spent_times.TimeExpensesQueries,
    work_breaks.WorkBreaksQueries,
):
    """Class representing list of all queries."""
