from django.urls import include, path

from apps.core.rest.routers import AppRouter
from .views import TimeExpensesView, UserProgressMetricsView, UserSalariesView, UserWorkBreaksView, WorkBreaksViewset

app_name = 'payroll'

router = AppRouter()
router.register('work-breaks', WorkBreaksViewset, basename='work-breaks')

urlpatterns = [
    path('users/<int:user_pk>/', include((
        [
            path('progress-metrics', UserProgressMetricsView.as_view(), name='progress-metrics'),
            path('salaries', UserSalariesView.as_view(), name='salaries'),
            path('time-expenses', TimeExpensesView.as_view(),
                 name='time-expenses'),
            path('work-breaks', UserWorkBreaksView.as_view(), name='user-work-breaks')
        ], app_name), 'users')),
    *router.urls
]
