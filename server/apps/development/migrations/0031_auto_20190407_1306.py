# Generated by Django 2.2 on 2019-04-07 10:06

import bitfield.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0030_auto_20190405_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammember',
            name='roles',
            field=bitfield.models.BitField((('leader', 'CH_LEADER'), ('developer', 'CH_DEVELOPER'), ('project_manager', 'CH_RM')), default=0),
        ),
    ]