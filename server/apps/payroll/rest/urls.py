from django.urls import include, path

from .views import TimeExpensesView, UserProgressMetricsView

app_name = 'payroll'

urlpatterns = [
    path('users/<int:user_pk>/', include((
        [
            path('progress-metrics', UserProgressMetricsView.as_view(), name='progress-metrics'),
            path('time-expenses', TimeExpensesView.as_view(),
                 name='time-expenses'),
        ], app_name), 'users'))
]
