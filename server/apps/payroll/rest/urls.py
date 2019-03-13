from django.urls import path, include

from .views import TimeExpensesView, UserMetricsView

app_name = 'payroll'

urlpatterns = [
    path('users/<int:user_pk>/', include((
        [
            path('metrics', UserMetricsView.as_view(), name='metrics'),
            path('time-expenses', TimeExpensesView.as_view(),
                 name='time-expenses'),
        ], app_name), 'users'))
]
