from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from rest_framework_swagger.views import get_swagger_view

from apps.core.utils.modules import get_module_url_patterns

admin.site.site_header = _('VN__ADMIN_DASHBOARD')

urlpatterns = [
    path('api/', include((get_module_url_patterns(
        'apps.users.rest.urls',
        'apps.development.rest.urls',
        'apps.payroll.rest.urls',
    ), 'urls'), namespace='api')),
    path('api/docs/', get_swagger_view(title='API'), name='swagger'),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
