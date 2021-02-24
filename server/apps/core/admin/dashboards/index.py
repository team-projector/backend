from jnt_admin_tools.dashboard import Dashboard, modules


class IndexDashboard(Dashboard):
    """Base class for dashboards."""

    def init_with_context(self, context):
        """Define what we need to see in admin dashboard here."""
        self.children.append(
            modules.AppList("Applications", exclude=["constance.*"]),
        )
        self.children.append(modules.RecentActions("Recent actions", 5))
