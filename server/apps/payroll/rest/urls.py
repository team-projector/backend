from django.urls import path

from apps.core.rest.routers import AppRouter
from .views import MetricsView, TimeExpensesView

app_name = 'payroll'

router = AppRouter()
router.register('time-expenses', TimeExpensesView, basename='time-expenses')

urlpatterns = [
    path('metrics', MetricsView.as_view(), name='metrics'),
    *router.urls
]
