from django.urls import path

from apps.core.rest.routers import AppRouter
from .views import IssuesViewset, gl_webhook, TeamsViewset, TeamMembersViewset

app_name = 'development'

router = AppRouter()
router.register('issues', IssuesViewset, basename='issues')
router.register(r'^teams/(?P<team_pk>\d+)/members$', TeamMembersViewset, basename='team-members')
router.register('teams', TeamsViewset, basename='teams')

urlpatterns = [
    path('gl-webhook', gl_webhook, name='gl-webhook'),
    *router.urls
]
