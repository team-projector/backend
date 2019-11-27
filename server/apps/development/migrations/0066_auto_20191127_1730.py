# Generated by Django 2.2.7 on 2019-11-27 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0065_auto_20191029_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='state',
            field=models.CharField(blank=True, choices=[('opened', 'CH_OPENED'), ('closed', 'CH_CLOSED')], help_text='HT__STATE', max_length=255, verbose_name='VN__STATE'),
        ),
        migrations.AlterField(
            model_name='mergerequest',
            name='state',
            field=models.CharField(blank=True, choices=[('opened', 'CH_OPENED'), ('merged', 'CH_MERGED'), ('closed', 'CH_CLOSED')], help_text='HT__STATE', max_length=255, verbose_name='VN__STATE'),
        ),
    ]
