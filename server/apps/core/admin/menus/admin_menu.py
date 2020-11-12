from django.urls import reverse_lazy
from jnt_admin_tools.menu import Menu, items
from django.utils.translation import gettext_lazy as _
from apps.core.admin.menus import AdminMenuItem

MANAGEMENT_MENU_ITEMS = (
    (_("VN__JOB_QUEUE"), "/admin/flower/", None),
    # _("Constance") - for lib constance
    (_("Constance"), reverse_lazy("admin:configuration"), None),
)


UTILS_MENU_ITEMS = (
    (_("VN__CLEAR_CACHE"), reverse_lazy("admin:clear-cache"), None),
    (
        _("VN__GENERATE_SALARIES"),
        reverse_lazy("admin:generate-salaries"),
        "payroll.add_salary",
    ),
    (_("VN__GRAPHQL_PLAYGROUND"), "/graphql/", None),
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
            items.MenuItem(_("VN__HOME"), reverse_lazy("admin:index")),
            items.AppList(title=_("VN__APPLICATIONS"), exclude=["constance.*"]),
            AdminMenuItem(_("VN__MANAGEMENT"), MANAGEMENT_MENU_ITEMS),
            AdminMenuItem(_("VN__UTILS"), UTILS_MENU_ITEMS),
        ]
