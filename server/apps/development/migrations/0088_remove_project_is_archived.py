# Generated by Django 3.1.2 on 2020-10-21 08:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0087_update_project_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='is_archived',
        ),
    ]
