from django.utils import timezone


from apps.payroll.models.mixins.approved import APPROVED, DECLINED
from apps.users.models import User


class WorkBreakManager:
    def __init__(self, work_break):
        self.work_break = work_break

    def approve(self,
                approved_by: User) -> None:
        self.work_break.approve_state = APPROVED
        self.work_break.approved_by = approved_by
        self.work_break.approved_at = timezone.now()
        self.work_break.save()

    def decline(self,
                approved_by: User,
                decline_reason: str) -> None:
        self.work_break.approve_state = DECLINED
        self.work_break.approved_by = approved_by
        self.work_break.approved_at = timezone.now()
        self.work_break.decline_reason = decline_reason
        self.work_break.save()
