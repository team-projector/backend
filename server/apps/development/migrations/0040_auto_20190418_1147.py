# -*- coding: utf-8 -*-

# Generated by Django 2.2 on 2019-04-18 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0039_auto_20190416_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='epic',
            name='milestone',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='epic', to='development.Milestone'),
        ),
    ]
