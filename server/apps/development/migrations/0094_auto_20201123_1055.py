# Generated by Django 3.1.2 on 2020-11-23 07:55

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('development', '0093_merge_project_members'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='projectmember',
            unique_together={('user', 'object_id', 'content_type')},
        ),
    ]