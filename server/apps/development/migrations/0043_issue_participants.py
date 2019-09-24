# -*- coding: utf-8 -*-

# Generated by Django 2.2 on 2019-04-26 15:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('development', '0042_auto_20190418_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='participant_issues', to=settings.AUTH_USER_MODEL),
        ),
    ]
