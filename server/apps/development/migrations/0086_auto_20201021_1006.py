# Generated by Django 3.1.2 on 2020-10-21 07:06

import jnt_django_toolbox.models.fields.enum
from django.db import migrations

import apps.development.models.milestone


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0085_auto_20201016_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milestone',
            name='state',
            field=jnt_django_toolbox.models.fields.enum.EnumField(blank=True, choices=[('ACTIVE', 'CH__STATE_ACTIVE'), ('CLOSED', 'CH__STATE_CLOSED')], enum=apps.development.models.milestone.MilestoneState, help_text='HT__STATE', verbose_name='VN__STATE'),
        ),
    ]
