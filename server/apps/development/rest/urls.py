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
    r'^milestones/(?P<milestone_pk>\d+)/features',
    views.MilestoneFeaturesViewset,
    'milestone-features'
)

urlpatterns = [
    path(
        'gl-webhook',
        views.gl_webhook,
        name='gl-webhook'
    ),
    *router.urls
]
