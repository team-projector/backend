from django.urls import include, path

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
    path('me/', include((
        [
            path(
                'user',
                views.MeUserView.as_view(),
                name='user'
            )
        ], app_name), 'me')),
    *router.urls
]
