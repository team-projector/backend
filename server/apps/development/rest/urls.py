from django.urls import path

from apps.core.rest.routers import AppRouter
from .views import IssuesViewset, gl_webhook, TeamsViewset, TeamMembersViewset, ProjectGroupMilestonesViewset, \
    ProjectMilestonesViewset

app_name = 'development'

router = AppRouter()
router.register('issues', IssuesViewset, basename='issues')
router.register(r'^project-groups/(?P<project_group_pk>\d+)/milestones$', ProjectGroupMilestonesViewset,
                basename='project-group-milestones')
router.register(r'^projects/(?P<project_pk>\d+)/milestones$', ProjectMilestonesViewset,
                basename='project-milestones')
router.register(r'^teams/(?P<team_pk>\d+)/members$', TeamMembersViewset, basename='team-members')
router.register('teams', TeamsViewset, basename='teams')

urlpatterns = [
    path('gl-webhook', gl_webhook, name='gl-webhook'),
    *router.urls
]
