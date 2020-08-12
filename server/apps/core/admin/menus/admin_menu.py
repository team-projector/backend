# -*- coding: utf-8 -*-

from django.urls import reverse
from jnt_admin_tools.menu import Menu, items

from apps.core.admin.menus import AdminMenuItem

MANAGEMENT_MENU_ITEMS = (("Job queue", "/admin/flower/", None),)

UTILS_MENU_ITEMS = (
    (
        "Generate salaries",
        reverse("admin:generate-salaries"),
        "payroll.add_salary",
    ),
    ("GraphQL playground", "/graphql/", None),
)


class AdminMenu(Menu):
    """A class representing menu admin dashboard."""

    def __init__(self, **kwargs):
        """
        Initialize self.

        Add menu item in Admin Dashboard.
        """
        super().__init__(**kwargs)

        self.children += [
            items.MenuItem("Home", reverse("admin:index")),
            items.AppList(title="Applications"),
            AdminMenuItem("Management", MANAGEMENT_MENU_ITEMS),
            AdminMenuItem("Utils", UTILS_MENU_ITEMS),
        ]
