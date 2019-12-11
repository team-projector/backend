# Generated by Django 2.2.7 on 2019-11-29 09:55

import bitfield.models
from django.db import migrations, models
from django.db.models.functions import Upper


def forwards(apps, schema_editor):
    to_change = [
        ('issue', ['state']),
        ('mergerequest', ['state']),
        ('milestone', ['state']),
        ('note', ['type']),
        ('projectmember', ['role']),
        ('ticket', ['type']),

    ]
    for model, fields in to_change:
        model_class = apps.get_model('development', model)
        updates = {f: Upper(f) for f in fields}
        model_class.objects.all().update(**updates)


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0066_auto_20191127_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='state',
            field=models.CharField(blank=True, choices=[('OPENED', 'CH_OPENED'), ('CLOSED', 'CH_CLOSED')], help_text='HT__STATE', max_length=255, verbose_name='VN__STATE'),
        ),
        migrations.AlterField(
            model_name='mergerequest',
            name='state',
            field=models.CharField(blank=True, choices=[('OPENED', 'CH_OPENED'), ('MERGED', 'CH_MERGED'), ('CLOSED', 'CH_CLOSED')], help_text='HT__STATE', max_length=255, verbose_name='VN__STATE'),
        ),
        migrations.AlterField(
            model_name='milestone',
            name='state',
            field=models.CharField(blank=True, choices=[('ACTIVE', 'active'), ('CLOSED', 'closed')], help_text='HT__STATE', max_length=20, verbose_name='VN__STATE'),
        ),
        migrations.AlterField(
            model_name='note',
            name='type',
            field=models.CharField(choices=[('TIME_SPEND', 'Time spend'), ('RESET_SPEND', 'Reset spend'), ('MOVED_FROM', 'Moved from')], help_text='HT__TYPE', max_length=20, verbose_name='VN__TYPE'),
        ),
        migrations.AlterField(
            model_name='projectmember',
            name='role',
            field=models.CharField(choices=[('DEVELOPER', 'CH_DEVELOPER'), ('PROJECT_MANAGER', 'CH_PM'), ('CUSTOMER', 'CH_CUSTOMER')], help_text='HT__ROLE', max_length=20, verbose_name='VN__ROLE'),
        ),
        migrations.AlterField(
            model_name='teammember',
            name='roles',
            field=bitfield.models.BitField((('LEADER', 'CH_LEADER'), ('DEVELOPER', 'CH_DEVELOPER'), ('WATCHER', 'CH_WATCHER')), default=0),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='type',
            field=models.CharField(blank=True, choices=[('FEATURE', 'CH_FEATURE'), ('IMPROVEMENT', 'CH_IMPROVEMENT'), ('BUG_FIXING', 'CH_BUG_FIXING')], help_text='HT__TYPE', max_length=50, verbose_name='VN__TYPE'),
        ),
        migrations.RunPython(forwards, backwards)
    ]