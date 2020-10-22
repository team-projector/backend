from django.urls import reverse_lazy
from jnt_admin_tools.menu import Menu, items

from apps.core.admin.menus import AdminMenuItem

MANAGEMENT_MENU_ITEMS = (
    ("Job queue", "/admin/flower/", None),
    ("Configuration", reverse_lazy("admin:configuration"), None),
)

UTILS_MENU_ITEMS = (
    ("Clear cache", reverse_lazy("admin:clear-cache"), None),
    (
        "Generate salaries",
        reverse_lazy("admin:generate-salaries"),
        "payroll.add_salary",
    ),
    ("GraphQL playground", "/graphql/", None),
)


class AdminMenu(Menu):
    """A class represents menu admin dashboard."""

    def __init__(self, **kwargs):
        """
        Initialize self.

        Add menu item in Admin Dashboard.
        """
        super().__init__(**kwargs)

        self.children += [
            items.MenuItem("Home", reverse_lazy("admin:index")),
            items.AppList(title="Applications"),
            AdminMenuItem("Management", MANAGEMENT_MENU_ITEMS),
            AdminMenuItem("Utils", UTILS_MENU_ITEMS),
        ]
