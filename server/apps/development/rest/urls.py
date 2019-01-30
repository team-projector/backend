from django.urls import path

from apps.core.rest.routers import AppRouter
from .views import IssuesViewset, MetricsView, gl_webhook

app_name = 'development'

router = AppRouter()
router.register('issues', IssuesViewset, basename='issues')

urlpatterns = [
    path('gl-webhook', gl_webhook, name='gl-webhook'),
    path('metrics', MetricsView.as_view(), name='metrics'),
    *router.urls,
]
