from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from rest_framework_swagger.views import get_swagger_view

admin.site.site_header = _('VN__ADMIN_DASHBOARD')

schema_view = get_swagger_view(title=str(_('VN__API')))

urlpatterns = [url('admin/', admin.site.urls),
               url('api/docs/', schema_view),
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
