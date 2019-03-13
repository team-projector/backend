from django.urls import path

from apps.core.rest.routers import AppRouter
from .views import UserMetricsView, TimeExpensesView

app_name = 'payroll'

router = AppRouter()
router.register('time-expenses', TimeExpensesView, basename='time-expenses')

urlpatterns = [
    path('users/<int:user_pk>/metrics', UserMetricsView.as_view(), name='user-metrics'),
    *router.urls
]
