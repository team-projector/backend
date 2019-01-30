from django.urls import include, path

from apps.core.rest.routers import AppRouter
from apps.users.rest.views import LoginView, LogoutView, MeUserView, UsersViewset

app_name = 'users'

router = AppRouter()
router.register('users', UsersViewset, basename='users')

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('me/', include((
        [
            path('user', MeUserView.as_view(), name='user')
        ], app_name), namespace='me')),
    *router.urls
]
