# Generated by Django 3.0.3 on 2020-02-14 13:56

import bitfield.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_auto_20191129_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='roles',
            field=bitfield.models.BitField([('DEVELOPER', 'CH_DEVELOPER'), ('TEAM_LEADER', 'CH_TEAM_LEADER'), ('PROJECT_MANAGER', 'CH_PROJECT_MANAGER'), ('CUSTOMER', 'CH_CUSTOMER'), ('SHAREHOLDER', 'CH_SHAREHOLDER')], default=0),
        ),
    ]
