from django.urls import path

from apps.core.rest.routers import AppRouter
from .views import IssuesViewset, gl_webhook, TeamsViewset

app_name = 'development'

router = AppRouter()
router.register('issues', IssuesViewset, basename='issues')
router.register('teams', TeamsViewset, basename='teams')

urlpatterns = [
    path('gl-webhook', gl_webhook, name='gl-webhook'),
    *router.urls
]
