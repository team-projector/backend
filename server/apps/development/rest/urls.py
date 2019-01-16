from django.urls import include, path

from .views import MeIssues, gl_webhook

app_name = 'development'

urlpatterns = [
    path('gl-webhook', gl_webhook, name='gl-webhook'),
    path('me/', include((
        [
            path('issues', MeIssues.as_view(), name='issues')
        ], app_name), namespace='me'))
]
