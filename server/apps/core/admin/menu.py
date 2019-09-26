# -*- coding: utf-8 -*-

from admin_tools.menu import Menu, items
from django.urls import reverse


class AdminMenu(Menu):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.children += [
            items.MenuItem('Home', reverse('admin:index')),
            items.AppList(title='Applications'),
            items.MenuItem('Management', children=[
                items.MenuItem('Job queue', '/admin/flower/'),
            ]),
            items.MenuItem('Utils', children=[
                items.MenuItem(
                    'Generate salaries',
                    reverse('admin:generate-salaries'),
                ),
            ]),
        ]
