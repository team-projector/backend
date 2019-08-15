from .workbreaks import (
    ApproveWorkBreakMutation, CreateWorkBreakMutation,
    DeclineWorkBreakMutation, DeleteWorkBreakMutation,
    UpdateWorkBreakMutation
)


class WorkBreaksMutations:
    approve_workbreak = ApproveWorkBreakMutation.Field()
    create_workbreak = CreateWorkBreakMutation.Field()
    decline_workbreak = DeclineWorkBreakMutation.Field()
    delete_workbreak = DeleteWorkBreakMutation.Field()
    update_workbreak = UpdateWorkBreakMutation.Field()
