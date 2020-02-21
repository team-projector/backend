# -*- coding: utf-8 -*-

from admin_tools.menu import Menu, items
from django.urls import reverse


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
            items.MenuItem("Management", children=[
                items.MenuItem("Job queue", "/admin/flower/"),
            ]),
            items.MenuItem("Utils", children=[
                items.MenuItem(
                    "Generate salaries",
                    reverse("admin:generate-salaries"),
                ),
                items.MenuItem(
                    "GraphQL playground",
                    "/graphql/",
                ),
            ]),
        ]
