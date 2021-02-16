import injector

from apps.users.logic import services


class ApplicationUserServicesModule(injector.Module):
    """Setup di for application services."""

    def configure(self, binder: injector.Binder) -> None:
        """Bind services."""
        binder.bind(
            services.IUserProblemsService,
            services.UserProblemsService,
            scope=injector.singleton,
        )

        binder.bind(
            services.IUserMetricsService,
            services.UserMetricsService,
            scope=injector.singleton,
        )
