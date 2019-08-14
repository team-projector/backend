from .workbreaks import (
    ApproveWorkBreakMutation, CreateWorkBreakMutation,
    DeclineWorkBreakMutation, UpdateWorkBreakMutation
)


class WorkBreaksMutations:
    approve_workbreak = ApproveWorkBreakMutation.Field()
    create_workbreak = CreateWorkBreakMutation.Field()
    decline_workbreak = DeclineWorkBreakMutation.Field()
    update_workbreak = UpdateWorkBreakMutation.Field()
