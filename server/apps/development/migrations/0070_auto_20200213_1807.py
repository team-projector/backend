# Generated by Django 3.0.2 on 2020-02-13 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0069_ticket_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='state',
            field=models.CharField(blank=True, choices=[('CREATED', 'CH_CREATED'), ('PLANNING', 'CH_PLANNING'), ('DOING', 'CH_DOING'), ('TESTING', 'CH_TESTING'), ('ACCEPTING', 'CH_ACCEPTING'), ('DONE', 'CH_DONE')], default='CREATED', help_text='HT__STATE', max_length=50, verbose_name='VN__STATE'),
        ),
    ]
