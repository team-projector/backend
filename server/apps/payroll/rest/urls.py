from django.urls import include, path

from apps.core.rest.routers import AppRouter
from . import views

app_name = 'payroll'

router = AppRouter()
router.register('work-breaks', views.WorkBreaksViewset, 'work-breaks')
router.register('salaries', views.SalariesViewSet, 'salaries')

urlpatterns = [
    path('users/<int:user_pk>/', include((
        [
            path(
                'progress-metrics',
                views.UserProgressMetricsView.as_view(),
                name='progress-metrics'
            ),
            path(
                'salaries',
                views.UserSalariesView.as_view(),
                name='salaries'
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
    path(
        'time-expenses',
        views.TimeExpensesView.as_view(),
        name='time-expenses'
    ),

    *router.urls
]
