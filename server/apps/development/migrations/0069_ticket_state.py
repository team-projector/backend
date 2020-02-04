# Generated by Django 2.2.9 on 2020-02-04 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0068_auto_20191218_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='state',
            field=models.CharField(blank=True, choices=[('CREATED', 'CH_CREATED'), ('PLANNING', 'CH_PLANNING'), ('DOING', 'CH_DOING'), ('TESTING', 'CH_TESTING'), ('ACCEPTING', 'CH_ACCEPTING'), ('DONE', 'CH_DONE')], help_text='HT__STATE', max_length=50, verbose_name='VN__STATE'),
        ),
    ]
