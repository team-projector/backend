from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.development.services.slack import send_msg_to_chanel
from apps.payroll.models.salary import Salary
from apps.payroll.services.salary.notifications import send_report_to_email


@receiver(post_save, sender=Salary)
def send_notification(instance, update_fields, **kwargs):
    if 'payed' in update_fields:
        send_report_to_email(instance)

        # TODO: move to function
        send_msg_to_chanel('#general',
                           f'Salary has been paid. ({instance.period_from} - {instance.period_to})')
