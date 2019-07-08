def is_salary_payed(salary):
    return salary.payed_tracker.changed().get('payed') is False
