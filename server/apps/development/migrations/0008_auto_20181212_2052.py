# -*- coding: utf-8 -*-

# Generated by Django 2.1.4 on 2018-12-12 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0007_project_full_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('full_title', 'title'), 'verbose_name': 'VN__PROJECT', 'verbose_name_plural': 'VN__PROJECTS'},
        ),
        migrations.AddField(
            model_name='project',
            name='gl_last_issues_sync',
            field=models.DateTimeField(blank=True, help_text='HT__GITLAB_LAST_ISSUES_SYNC', null=True, verbose_name='VN__GITLAB_LAST_ISSUES_SYNC'),
        ),
    ]
