# -*- coding: utf-8 -*-

# Generated by Django 2.2 on 2019-04-08 09:23

import jnt_django_toolbox.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("development", "0031_auto_20190407_1306"),
    ]

    operations = [
        migrations.AlterField(
            model_name="teammember",
            name="roles",
            field=jnt_django_toolbox.models.fields.BitField((("leader", "CH_LEADER"), ("developer", "CH_DEVELOPER")), default=0),
        ),
    ]
