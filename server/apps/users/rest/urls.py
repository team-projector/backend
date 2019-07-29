from django.urls import include, path

from . import views

app_name = 'users'

urlpatterns = [
    path('me/', include((
        [
            path(
                'user',
                views.MeUserView.as_view(),
                name='user'
            )
        ], app_name), 'me')),
]
