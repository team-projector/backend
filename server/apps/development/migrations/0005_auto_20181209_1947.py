# -*- coding: utf-8 -*-

# Generated by Django 2.1.4 on 2018-12-09 19:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("development", "0004_auto_20181208_1831"),
    ]

    operations = [
        migrations.RenameField(
            model_name="issue",
            old_name="gitlab_id",
            new_name="gl_id",
        ),
        migrations.RenameField(
            model_name="issue",
            old_name="gitlab_last_sync",
            new_name="gl_last_sync",
        ),
        migrations.RenameField(
            model_name="issue",
            old_name="gitlab_url",
            new_name="gl_url",
        ),
        migrations.RenameField(
            model_name="project",
            old_name="gitlab_id",
            new_name="gl_id",
        ),
        migrations.RenameField(
            model_name="project",
            old_name="gitlab_last_sync",
            new_name="gl_last_sync",
        ),
        migrations.RenameField(
            model_name="project",
            old_name="gitlab_url",
            new_name="gl_url",
        ),
        migrations.RenameField(
            model_name="projectgroup",
            old_name="gitlab_id",
            new_name="gl_id",
        ),
        migrations.RenameField(
            model_name="projectgroup",
            old_name="gitlab_last_sync",
            new_name="gl_last_sync",
        ),
        migrations.RenameField(
            model_name="projectgroup",
            old_name="gitlab_url",
            new_name="gl_url",
        ),
    ]
