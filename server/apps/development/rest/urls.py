from django.urls import path

from apps.core.rest.routers import AppRouter
from .views import (
    FeatureIssuesViewset, FeaturesViewset, GitlabIssueStatusView, GitlabStatusView, IssuesViewset,
    MilestoneFeaturesViewset, MilestoneIssuesViewset, MilestoneIssuesOrphanViewset, MilestonesViewset,
    TeamIssueProblemsViewset, TeamMembersViewset, TeamsViewset, gl_webhook
)

app_name = 'development'

router = AppRouter()
router.register('features', FeaturesViewset, basename='features')
router.register('issues', IssuesViewset, basename='issues')
router.register(r'^features/(?P<feature_pk>\d+)/issues$', FeatureIssuesViewset,
                basename='milestone-issues')
router.register(r'^milestones/(?P<milestone_pk>\d+)/issues$', MilestoneIssuesViewset,
                basename='milestone-issues')
router.register(r'^milestones/(?P<milestone_pk>\d+)/issues/orphan$', MilestoneIssuesOrphanViewset,
                basename='milestone-issues-orphan')
router.register(r'^milestones/(?P<milestone_pk>\d+)/features', MilestoneFeaturesViewset,
                basename='features-issues')
router.register(r'^teams/(?P<team_pk>\d+)/members$', TeamMembersViewset, basename='team-members')
router.register(r'^teams/(?P<team_pk>\d+)/problems$', TeamIssueProblemsViewset, basename='team-problems')
router.register('teams', TeamsViewset, basename='teams')
router.register('milestones', MilestonesViewset, basename='milestones')

urlpatterns = [
    path('gitlab/status', GitlabStatusView.as_view(), name='gitlab-status'),
    path('gitlab/issue/status', GitlabIssueStatusView.as_view(), name='gitlab-issue-status'),
    path('gl-webhook', gl_webhook, name='gl-webhook'),
    *router.urls
]
