from django.urls import include, path

from .views import MeIssues

app_name = 'development'

urlpatterns = [
    path('me/', include((
        [
            path('issues', MeIssues.as_view(), name='issues')
        ], app_name), namespace='me'))
]
