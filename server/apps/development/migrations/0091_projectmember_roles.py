# Generated by Django 3.1.2 on 2020-11-20 12:18

from django.db import migrations
import jnt_django_toolbox.models.fields.bit.field


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0090_projectgroup_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectmember',
            name='roles',
            field=jnt_django_toolbox.models.fields.bit.field.BitField([('DEVELOPER', 'CH__DEVELOPER'), ('MANAGER', 'CH__MANAGER'), ('CUSTOMER', 'CH__CUSTOMER')], default=0),
        ),
    ]
