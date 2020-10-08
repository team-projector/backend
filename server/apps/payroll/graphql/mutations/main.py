from apps.payroll.graphql.mutations import work_breaks


class PayrollMutations:
    """Class representing list of all mutations."""

    approve_work_break = work_breaks.ApproveWorkBreakMutation.Field()
    create_work_break = work_breaks.CreateWorkBreakMutation.Field()
    decline_work_break = work_breaks.DeclineWorkBreakMutation.Field()
    delete_work_break = work_breaks.DeleteWorkBreakMutation.Field()
    update_work_break = work_breaks.UpdateWorkBreakMutation.Field()
