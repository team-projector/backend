# Generated by Django 3.1.2 on 2020-10-21 08:25

import jnt_django_toolbox.models.fields.enum
from django.db import migrations

import apps.development.models.project


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0085_auto_20201016_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='state',
            field=jnt_django_toolbox.models.fields.enum.EnumField(choices=[('DEVELOPING', 'CH__DEVELOPING'), ('SUPPORTING', 'CH__SUPPORTING'), ('ARCHIVED', 'CH__ARCHIVED')], default='DEVELOPING', enum=apps.development.models.project.ProjectState, help_text='HT__STATE', verbose_name='VN__STATE'),
        ),
    ]
