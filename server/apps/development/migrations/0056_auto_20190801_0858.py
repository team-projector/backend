# -*- coding: utf-8 -*-

# Generated by Django 2.2.2 on 2019-08-01 05:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('development', '0055_auto_20190719_1443'),
    ]

    operations = [
        migrations.AddField(
            model_name='mergerequest',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='participant_merge_requests', to=settings.AUTH_USER_MODEL),
        ),
    ]
