# Generated by Django 2.1.4 on 2018-12-16 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0008_auto_20181212_2052'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectgroup',
            name='full_title',
            field=models.CharField(blank=True, help_text='HT__FULL_TITLE', max_length=255, null=True, verbose_name='VN__FULL_TITLE'),
        ),
    ]
