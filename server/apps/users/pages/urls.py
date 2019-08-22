from django.urls import path
from social_django import views

app_name = 'social'

urlpatterns = [
    path(
        'login/<slug:backend>/',
        views.auth,
        name='begin'
    ),
    # path(
    #     'complete/<slug:backend>/',
    #     auth_complete,
    #     name='complete'
    # ),
    # path(
    #     'disconnect/<slug:backend>/',
    #     views.disconnect,
    #     name='disconnect'
    # ),
    # path(
    #     'disconnect/<slug:backend>/<int:association_id>/',
    #     views.disconnect,
    #     name='disconnect_individual'
    # ),
]
