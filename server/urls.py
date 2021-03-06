from constance.admin import Config
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from apps.core.admin.views import ClearCacheAdminView
from apps.core.pages.views.backend_config import BackendConfigView
from gql import get_api_graphql_view, get_graphql_view

admin.site.site_header = _("VN__ADMIN_DASHBOARD")
admin.site.enable_nav_sidebar = False

constance_admin = admin.site._registry.get(Config)  # noqa:WPS437

admin_urls = (
    *admin.site.urls[0],
    path(
        "configuration/",
        constance_admin.admin_site.admin_view(constance_admin.changelist_view),
        name="configuration",
    ),
    path("clear-cache", ClearCacheAdminView.as_view(), name="clear-cache"),
)
urlpatterns = [
    path("ht/", include("health_check.urls")),
    path("graphql/", get_graphql_view()),
    path("api/graphql", csrf_exempt(get_api_graphql_view())),
    path("api/", include("apps.development.api.urls", namespace="api")),
    path("api/", include("apps.users.pages.urls", namespace="social")),
    path("admin_tools/", include("jnt_admin_tools.urls")),
    path("admin/", include((admin_urls, "admin"))),
    path(
        "backend/config.js",
        BackendConfigView.as_view(),
        name="backend-config",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
