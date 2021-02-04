from apps.payroll.services.spent_time.updater import adjust_spents_times
from celery_app import app


@app.task(queue="low_priority")
def adjust_spents_times_task():
    """Adjust spents times task."""
    adjust_spents_times()
