from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.payroll.models.salary import Salary
from apps.payroll.services.salary.notifications import send_report_to_email


@receiver(post_save, sender=Salary)
def send_notification(instance, update_fields, **kwargs):
    if update_fields and 'payed' in update_fields and instance.payed:
        send_report_to_email(instance, instance.user.email)
