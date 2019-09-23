from .work_breaks import (
    ApproveWorkBreakMutation, CreateWorkBreakMutation,
    DeclineWorkBreakMutation, DeleteWorkBreakMutation,
    UpdateWorkBreakMutation,
)


class WorkBreaksMutations:
    approve_work_break = ApproveWorkBreakMutation.Field()
    create_work_break = CreateWorkBreakMutation.Field()
    decline_work_break = DeclineWorkBreakMutation.Field()
    delete_work_break = DeleteWorkBreakMutation.Field()
    update_work_break = UpdateWorkBreakMutation.Field()
