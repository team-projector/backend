from django.urls import include, path

from .views import TimeExpensesView, UserProgressMetricsView, UserSalariesView

app_name = 'payroll'

urlpatterns = [
    path('users/<int:user_pk>/', include((
        [
            path('progress-metrics', UserProgressMetricsView.as_view(), name='progress-metrics'),
            path('salaries', UserSalariesView.as_view(), name='salaries'),
            path('time-expenses', TimeExpensesView.as_view(),
                 name='time-expenses'),
        ], app_name), 'users'))
]
