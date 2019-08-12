from .workbreaks import ApproveWorkBreakMutation, DeclineWorkBreakMutation


class WorkBreaksMutations:
    approve_workbreak = ApproveWorkBreakMutation.Field()
    decline_workbreak = DeclineWorkBreakMutation.Field()
