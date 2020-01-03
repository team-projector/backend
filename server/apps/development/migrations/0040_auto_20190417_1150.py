# -*- coding: utf-8 -*-

# Generated by Django 2.2 on 2019-04-17 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("development", "0039_auto_20190416_1757"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="gl_iid",
            field=models.PositiveIntegerField(help_text="HT__GITLAB_INTERNAL_ID", null=True, verbose_name="VN__GITLAB_INTERNAL_ID"),
        ),
        migrations.AddField(
            model_name="milestone",
            name="gl_iid",
            field=models.PositiveIntegerField(help_text="HT__GITLAB_INTERNAL_ID", null=True, verbose_name="VN__GITLAB_INTERNAL_ID"),
        ),
        migrations.AddField(
            model_name="project",
            name="gl_iid",
            field=models.PositiveIntegerField(help_text="HT__GITLAB_INTERNAL_ID", null=True, verbose_name="VN__GITLAB_INTERNAL_ID"),
        ),
        migrations.AddField(
            model_name="projectgroup",
            name="gl_iid",
            field=models.PositiveIntegerField(help_text="HT__GITLAB_INTERNAL_ID", null=True, verbose_name="VN__GITLAB_INTERNAL_ID"),
        ),
    ]
