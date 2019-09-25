# -*- coding: utf-8 -*-

# Generated by Django 2.1.7 on 2019-03-11 10:26

import bitfield.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('development', '0020_auto_20190310_1219'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='HT__TITLE', max_length=255, verbose_name='VN__TITLE')),
            ],
            options={
                'verbose_name': 'VN__TEAM',
                'verbose_name_plural': 'VN__TEAMS',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roles', bitfield.models.BitField((('leader', 'CH_LEADER'), ('developer', 'CH_DEVELOPER')), default=0)),
                ('team', models.ForeignKey(help_text='HT__TEAM', on_delete=django.db.models.deletion.CASCADE, related_name='members', to='development.Team', verbose_name='VN__TEAM')),
                ('user', models.ForeignKey(help_text='HT__USER', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='VN__USER')),
            ],
            options={
                'verbose_name': 'VN__TEAM_MEMBER',
                'verbose_name_plural': 'VN__TEAM_MEMBERS',
                'ordering': ('team', 'user'),
            },
        ),
        migrations.AlterField(
            model_name='note',
            name='user',
            field=models.ForeignKey(blank=True, help_text='HT__USER', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='VN__USER'),
        ),
    ]
