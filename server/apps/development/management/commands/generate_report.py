# -*- coding: utf-8 -*-

from decimal import Decimal
from itertools import groupby

import xlsxwriter
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from xlsxwriter.utility import xl_range

from apps.development.models import Issue, Project, ProjectGroup
from apps.users.models import User


class Command(BaseCommand):
    project_cache = {}
    group_cache = {}
    user_cache = {}

    def handle(self, *args, **options):
        workbook = xlsxwriter.Workbook('costs_report.xlsx', {
            'default_date_format': 'dd/mm/yy'
        })
        worksheet = workbook.add_worksheet()

        project_format = workbook.add_format({
            'bg_color': '#d1e0e3'
        })
        group_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'bg_color': '#fef2cc',
        })

        total_format = workbook.add_format({
            'bg_color': '#c9daf8',
            'num_format': '#,##0',
        })

        group_total_format = workbook.add_format({
            'bg_color': '#c9daf8',
            'num_format': '#,##0',
            'bold': True
        })

        track_format = workbook.add_format({
            'num_format': '#,##0',
        })

        month_format = workbook.add_format({
            'num_format': 'mm/yy',
            'align': 'center',
        })

        data = list(self.load_data())

        start_date = min(data, key=lambda i: i['month'])['month']
        finish_date = max(data, key=lambda i: i['month'])['month']

        curr_date = start_date
        last_col = 1

        dates = []

        while curr_date <= finish_date:
            dates.append(curr_date)

            curr_date += relativedelta(months=+1)

        for d in dates:
            worksheet.write(0, last_col, d.strftime('%m/%y'), month_format)
            last_col += 1

        worksheet.freeze_panes(1, 0)

        current_row = 1

        for group, group_data in groupby(data, lambda i: self.get_project(i['project']).group):
            worksheet.merge_range(current_row, 0, current_row, last_col, group.full_title, group_format)

            start_row = current_row

            current_row += 1

            for project, project_data in groupby(group_data, lambda i: self.get_project(i['project'])):
                worksheet.merge_range(current_row, 0, current_row, last_col, project.title, project_format)

                current_row += 1

                for employee, track_data in groupby(project_data, lambda i: self.get_user(i['employee'])):
                    worksheet.write(current_row, 0, employee.login)

                    for track in track_data:
                        hours = track['spent_time'] / (60 * 60)
                        salary = int(Decimal(hours) * employee.hour_rate)
                        if salary:
                            worksheet.write_number(current_row,
                                                   dates.index(track['month']) + 1,
                                                   salary,
                                                   track_format)

                    worksheet.write(current_row,
                                    last_col,
                                    f'=SUM({xl_range(current_row, 1, current_row, last_col - 1)})',
                                    total_format)

                    current_row += 1

            for i in range(1, len(dates) + 1):
                worksheet.write(current_row,
                                i,
                                f'=SUM({xl_range(start_row, i, current_row - 1, i)})',
                                total_format)

            worksheet.write(current_row,
                            last_col,
                            f'=SUM({xl_range(start_row, last_col, current_row - 1, last_col)})',
                            group_total_format)

            current_row += 1

        workbook.close()

    def load_data(self):
        return Issue.objects.annotate(month=TruncMonth('created_at')) \
            .filter(user__isnull=False, month__isnull=False) \
            .values('month', 'project', 'user') \
            .annotate(spent_time=Sum('total_time_spent')) \
            .order_by('project', 'user', 'month')

    def get_project(self, id):
        if id not in self.project_cache:
            self.project_cache[id] = Project.objects.get(id=id)

        return self.project_cache[id]

    def get_group(self, id):
        if id not in self.group_cache:
            self.group_cache[id] = ProjectGroup.objects.get(id=id)

        return self.group_cache[id]

    def get_user(self, id):
        if id not in self.user_cache:
            self.user_cache[id] = User.objects.get(id=id)

        return self.user_cache[id]
