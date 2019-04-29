from django.urls import path

from apps.core.rest.routers import AppRouter
from .views import (
    IssuesViewset, gl_webhook, TeamsViewset, TeamMembersViewset, ProjectGroupMilestonesViewset,
    ProjectMilestonesViewset, MilestoneIssuesViewset, MilestoneEpicsViewset, EpicsViewset, EpicIssuesViewset,
    GitlabStatusView
)

app_name = 'development'

router = AppRouter()
router.register('epics', EpicsViewset, basename='epics')
router.register('issues', IssuesViewset, basename='issues')
router.register(r'^epics/(?P<epic_pk>\d+)/issues$', EpicIssuesViewset,
                basename='milestone-issues')
router.register(r'^project-groups/(?P<project_group_pk>\d+)/milestones', ProjectGroupMilestonesViewset,
                basename='project-group-milestones')
router.register(r'^projects/(?P<project_pk>\d+)/milestones$', ProjectMilestonesViewset,
                basename='project-milestones')
router.register(r'^milestones/(?P<milestone_pk>\d+)/issues$', MilestoneIssuesViewset,
                basename='milestone-issues')
router.register(r'^milestones/(?P<milestone_pk>\d+)/epics', MilestoneEpicsViewset,
                basename='epics-issues')
router.register(r'^teams/(?P<team_pk>\d+)/members$', TeamMembersViewset, basename='team-members')
router.register('teams', TeamsViewset, basename='teams')

urlpatterns = [
    path('gitlab/status', GitlabStatusView.as_view(), name='gitlab-status'),
    path('gl-webhook', gl_webhook, name='gl-webhook'),
    *router.urls
]
