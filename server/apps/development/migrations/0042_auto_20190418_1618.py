# Generated by Django 2.2 on 2019-04-18 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0041_merge_20190418_1612'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='gl_iid',
        ),
        migrations.RemoveField(
            model_name='projectgroup',
            name='gl_iid',
        ),
    ]
