from django.urls import path

from .views import MetricsView

app_name = 'payroll'

urlpatterns = [
    path('metrics', MetricsView.as_view(), name='metrics'),
]
