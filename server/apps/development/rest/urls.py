from django.urls import path

from apps.core.rest.routers import AppRouter
from .views import (
    FeatureIssuesViewset, FeaturesViewset, GitlabIssueStatusView, GitlabStatusView, IssuesViewset,
    MilestoneFeaturesViewset, MilestoneIssuesOrphanViewset, MilestoneIssuesViewset, MilestonesViewset,
    TeamIssueProblemsViewset, TeamIssuesViewset, TeamMembersViewset, TeamsViewset, gl_webhook
)

app_name = 'development'

router = AppRouter()
router.register('features', FeaturesViewset, 'features')
router.register('issues', IssuesViewset, 'issues')
router.register(r'^features/(?P<feature_pk>\d+)/issues$', FeatureIssuesViewset, 'milestone-issues')

router.register(r'^milestones/(?P<milestone_pk>\d+)/issues$', MilestoneIssuesViewset, 'milestone-issues')
router.register(r'^milestones/(?P<milestone_pk>\d+)/issues/orphan$', MilestoneIssuesOrphanViewset,
                'milestone-issues-orphan')
router.register(r'^milestones/(?P<milestone_pk>\d+)/features', MilestoneFeaturesViewset, 'features-issues')
router.register('milestones', MilestonesViewset, 'milestones')

router.register(r'^teams/(?P<team_pk>\d+)/issues$', TeamIssuesViewset, 'team-issues')
router.register(r'^teams/(?P<team_pk>\d+)/members$', TeamMembersViewset, 'team-members')
router.register(r'^teams/(?P<team_pk>\d+)/problems$', TeamIssueProblemsViewset, 'team-problems')
router.register('teams', TeamsViewset, 'teams')

urlpatterns = [
    path('gitlab/status', GitlabStatusView.as_view(), name='gitlab-status'),
    path('gitlab/issue/status', GitlabIssueStatusView.as_view(), name='gitlab-issue-status'),
    path('gl-webhook', gl_webhook, name='gl-webhook'),
    *router.urls
]
