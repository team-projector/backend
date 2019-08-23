from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from gql import get_graphql_view, get_api_graphql_view

admin.site.site_header = _('VN__ADMIN_DASHBOARD')

urlpatterns = [
    path('ht/', include('health_check.urls')),
    path('graphql', get_graphql_view()),
    path('api/graphql', csrf_exempt(get_api_graphql_view())),
    path('api/', include('apps.development.api.urls', namespace='api')),
    path('api/', include('apps.users.pages.urls', namespace='social')),
    path('admin_tools/', include('admin_tools.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
