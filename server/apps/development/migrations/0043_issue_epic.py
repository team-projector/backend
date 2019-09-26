# -*- coding: utf-8 -*-

# Generated by Django 2.2 on 2019-04-25 12:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0042_auto_20190418_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='epic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='development.Epic'),
        ),
    ]
