# Generated by Django 3.1.2 on 2020-11-23 09:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0095_remove_projectmember_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='team',
            field=models.ForeignKey(blank=True, help_text='HT__TEAM', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects', to='development.team', verbose_name='VN__TEAM'),
        ),
        migrations.AddField(
            model_name='projectgroup',
            name='team',
            field=models.ForeignKey(blank=True, help_text='HT__TEAM', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_groups', to='development.team', verbose_name='VN__TEAM'),
        ),
    ]
