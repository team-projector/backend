# -*- coding: utf-8 -*-

from django.utils import timezone

from apps.payroll.models.mixins.approved import ApprovedState
from apps.users.models import User


class Manager:
    """The Work Break manager."""

    def __init__(self, work_break):
        """Initialize self."""
        self.work_break = work_break

    def approve(self, approved_by: User) -> None:
        """Approve work break."""
        self.work_break.approve_state = ApprovedState.APPROVED
        self.work_break.approved_by = approved_by
        self.work_break.approved_at = timezone.now()
        self.work_break.save()

    def decline(
        self,
        approved_by: User,
        decline_reason: str,
    ) -> None:
        """Decline work break."""
        self.work_break.approve_state = ApprovedState.DECLINED
        self.work_break.approved_by = approved_by
        self.work_break.approved_at = timezone.now()
        self.work_break.decline_reason = decline_reason
        self.work_break.save()
