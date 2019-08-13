from apps.core.rest.routers import AppRouter
from . import views

app_name = 'payroll'

router = AppRouter()
router.register(
    'work-breaks',
    views.WorkBreaksViewset,
    'work-breaks'
)

urlpatterns = [
    *router.urls
]
