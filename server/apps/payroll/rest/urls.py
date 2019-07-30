from django.urls import include, path

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
    path('users/<int:user_pk>/', include((
        [
            path(
                'progress-metrics',
                views.UserProgressMetricsView.as_view(),
                name='progress-metrics'
            ),
        ], app_name), 'users')),
    path('teams/<int:team_pk>/', include((
        [
            path(
                'progress-metrics',
                views.TeamProgressMetricsView.as_view(),
                name='progress-metrics'
            ),
        ], app_name), 'teams')),

    *router.urls
]
