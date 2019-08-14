from django.urls import path

from apps.core.rest.routers import AppRouter
from . import views

app_name = 'development'

router = AppRouter()
router.register(
    'features',
    views.FeaturesViewset,
    'features'
)
router.register(
    r'^features/(?P<feature_pk>\d+)/issues$',
    views.FeatureIssuesViewset,
    'milestone-issues'
)

router.register(
    r'^milestones/(?P<milestone_pk>\d+)/features',
    views.MilestoneFeaturesViewset,
    'milestone-features'
)

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

urlpatterns = [
    path(
        'gl-webhook',
        views.gl_webhook,
        name='gl-webhook'
    ),
    *router.urls
]
