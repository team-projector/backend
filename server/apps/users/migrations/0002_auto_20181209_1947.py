# -*- coding: utf-8 -*-

# Generated by Django 2.1.4 on 2018-12-09 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gl_avatar',
            field=models.URLField(blank=True, help_text='HT__GITLAB_AVATAR', null=True, unique=True, verbose_name='VN__GITLAB_AVATAR'),
        ),
        migrations.AddField(
            model_name='user',
            name='gl_id',
            field=models.PositiveIntegerField(blank=True, help_text='HT__GITLAB_ID', null=True, verbose_name='VN__GITLAB_ID'),
        ),
        migrations.AddField(
            model_name='user',
            name='gl_last_sync',
            field=models.DateTimeField(blank=True, help_text='HT__GITLAB_LAST_SYNC', null=True, verbose_name='VN__GITLAB_LAST_SYNC'),
        ),
        migrations.AddField(
            model_name='user',
            name='gl_url',
            field=models.URLField(blank=True, help_text='HT__GITLAB_URL', null=True, verbose_name='VN__GITLAB_URL'),
        ),
        migrations.AddField(
            model_name='user',
            name='gl_username',
            field=models.CharField(blank=True, help_text='HT__GITLAB_USERNAME', max_length=50, null=True, unique=True, verbose_name='VN__GITLAB_USERNAME'),
        ),
    ]
