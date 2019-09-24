# -*- coding: utf-8 -*-

from django.urls import path

from . import views

app_name = 'development'

urlpatterns = [
    path(
        'gl-webhook',
        views.gl_webhook,
        name='gl-webhook',
    ),
]
