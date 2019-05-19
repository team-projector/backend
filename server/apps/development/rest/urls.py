from django.urls import path

from apps.core.rest.routers import AppRouter
from .views import (
    IssuesViewset, gl_webhook, TeamsViewset, TeamMembersViewset, ProjectGroupMilestonesViewset,
    ProjectMilestonesViewset, MilestoneIssuesViewset, MilestoneFeaturesViewset, FeaturesViewset, FeatureIssuesViewset,
    GitlabStatusView, MilestonesViewset, GitlabIssueStatusView
)

app_name = 'development'

router = AppRouter()
router.register('features', FeaturesViewset, basename='features')
router.register('issues', IssuesViewset, basename='issues')
router.register(r'^features/(?P<feature_pk>\d+)/issues$', FeatureIssuesViewset,
                basename='milestone-issues')
router.register(r'^project-groups/(?P<project_group_pk>\d+)/milestones', ProjectGroupMilestonesViewset,
                basename='project-group-milestones')
router.register(r'^projects/(?P<project_pk>\d+)/milestones$', ProjectMilestonesViewset,
                basename='project-milestones')
router.register(r'^milestones/(?P<milestone_pk>\d+)/issues$', MilestoneIssuesViewset,
                basename='milestone-issues')
router.register(r'^milestones/(?P<milestone_pk>\d+)/features', MilestoneFeaturesViewset,
                basename='features-issues')
router.register(r'^teams/(?P<team_pk>\d+)/members$', TeamMembersViewset, basename='team-members')
router.register('teams', TeamsViewset, basename='teams')
router.register('milestones', MilestonesViewset, basename='milestones')

urlpatterns = [
    path('gitlab/status', GitlabStatusView.as_view(), name='gitlab-status'),
    path('gitlab/issue/status', GitlabIssueStatusView.as_view(), name='gitlab-issue-status'),
    path('gl-webhook', gl_webhook, name='gl-webhook'),
    *router.urls
]
