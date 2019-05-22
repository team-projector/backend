from django.urls import include, path

from apps.core.rest.routers import AppRouter
from .views import (
    TeamProgressMetricsView, TimeExpensesView, UserProgressMetricsView, UserSalariesView,
    UserWorkBreaksView, WorkBreaksViewset, SalariesViewSet, SalariesTimeExpensesViewSet
)

app_name = 'payroll'

router = AppRouter()
router.register('work-breaks', WorkBreaksViewset, basename='work-breaks')
router.register('salaries', SalariesViewSet, basename='salaries')
router.register(r'^salaries/(?P<salary_pk>\d+)/time-expenses$', SalariesTimeExpensesViewSet,
                basename='salaries-time-expenses')

urlpatterns = [
    path('users/<int:user_pk>/', include((
        [
            path('progress-metrics', UserProgressMetricsView.as_view(), name='progress-metrics'),
            path('salaries', UserSalariesView.as_view(), name='salaries'),
            path('time-expenses', TimeExpensesView.as_view(),
                 name='time-expenses'),
            path('work-breaks', UserWorkBreaksView.as_view(), name='user-work-breaks')
        ], app_name), 'users')),
    path('teams/<int:team_pk>/', include((
        [
            path('progress-metrics', TeamProgressMetricsView.as_view(), name='progress-metrics'),
        ], app_name), 'teams')),
    *router.urls
]
