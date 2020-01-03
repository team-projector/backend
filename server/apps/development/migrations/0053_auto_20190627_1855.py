# -*- coding: utf-8 -*-

# Generated by Django 2.2.2 on 2019-06-27 15:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("development", "0052_auto_20190611_1321"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="teammember",
            options={"verbose_name": "VN__TEAM_MEMBER", "verbose_name_plural": "VN__TEAM_MEMBERS"},
        ),
        migrations.AddField(
            model_name="team",
            name="members",
            field=models.ManyToManyField(related_name="teams", through="development.TeamMember", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="teammember",
            name="team",
            field=models.ForeignKey(help_text="HT__TEAM", on_delete=django.db.models.deletion.CASCADE, to="development.Team", verbose_name="VN__TEAM"),
        ),
        migrations.AlterField(
            model_name="teammember",
            name="user",
            field=models.ForeignKey(help_text="HT__USER", on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="VN__USER"),
        ),
        migrations.AlterUniqueTogether(
            name="teammember",
            unique_together=set(),
        ),
    ]
