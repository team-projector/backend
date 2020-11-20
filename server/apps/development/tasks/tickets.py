from apps.development.models import Ticket
from apps.development.services.ticket.state import ticket_completion_service
from celery_app import app


@app.task
def notify_if_ticket_completed_task(ticket_pk):
    """Send notifications to the users if a ticket is completed."""
    ticket = Ticket.objects.filter(pk=ticket_pk).first()
    if not ticket:
        return

    ticket_completion_service.notify_if_completed(ticket)
