from apps.core.rest.routers import AppRouter
from . import views

app_name = 'users'

router = AppRouter()
router.register(
    'users',
    views.UsersViewset,
    'users'
)

urlpatterns = [
    *router.urls
]
