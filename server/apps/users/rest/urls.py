from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.rest.views import LoginView, LogoutView, MeUserView

app_name = 'users'

router = DefaultRouter(trailing_slash=False)

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('me/', include((
        [
            path('user', MeUserView.as_view(), name='user')
        ], app_name), namespace='me')),
    path('', include(router.urls)),
]
