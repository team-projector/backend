from django.urls import path

from apps.core.rest.routers import AppRouter
from . import views

app_name = 'development'

router = AppRouter()
router.register('features', views.FeaturesViewset, 'features')
router.register('issues', views.IssuesViewset, 'issues')
router.register(
    r'^features/(?P<feature_pk>\d+)/issues$',
    views.FeatureIssuesViewset,
    'milestone-issues'
)

router.register(
    r'^milestones/(?P<milestone_pk>\d+)/issues$',
    views.MilestoneIssuesViewset,
    'milestone-issues'
)
router.register(
    r'^milestones/(?P<milestone_pk>\d+)/issues/orphan$',
    views.MilestoneIssuesOrphanViewset,
    'milestone-issues-orphan'
)
router.register(
    r'^milestones/(?P<milestone_pk>\d+)/features',
    views.MilestoneFeaturesViewset,
    'features-issues'
)
router.register('milestones', views.MilestonesViewset, 'milestones')

router.register(
    r'^teams/(?P<team_pk>\d+)/issues$',
    views.TeamIssuesViewset,
    'team-issues'
)
router.register(
    r'^teams/(?P<team_pk>\d+)/members$',
    views.TeamMembersViewset,
    'team-members'
)

router.register('teams', views.TeamsViewset, 'teams')

urlpatterns = [
    path(
        'gitlab/status',
        views.GitlabStatusView.as_view(),
        name='gitlab-status'
    ),
    path(
        'gitlab/issue/status',
        views.GitlabIssueStatusView.as_view(),
        name='gitlab-issue-status'
    ),
    path(
        'gl-webhook',
        views.gl_webhook,
        name='gl-webhook'
    ),
    *router.urls
]
