# -*- coding: utf-8 -*-
import datetime

from django.core.management.base import BaseCommand

from apps.payroll.models import SpentTime
from apps.users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects.filter(is_active=True):
            self._handle_user(user)

    def _handle_user(self, user):
        times = SpentTime.objects.filter(
            salary__isnull=True,
            user=user,
            date__lt=datetime.date(2019, 1, 1),
        )

        if not times.exists():
            return

        print(f'user: {user}; ', end='')
        print(f'times: {times.count()}, ')

        salary = user.salaries.order_by('created_at').first()
        if salary:
            times.update(salary=salary)
            print(f'salary: {salary}')



        t = 0
