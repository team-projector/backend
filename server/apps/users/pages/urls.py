# -*- coding: utf-8 -*-

from django.urls import path
from social_django import views

from apps.users.pages.views import auth_complete

app_name = 'social'

urlpatterns = [
    path(
        'login/<slug:backend>/',
        views.auth,
        name='begin',
    ),
    path(
        'complete/<slug:backend>/',
        auth_complete,
        name='complete',
    ),
]
