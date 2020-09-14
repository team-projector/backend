# Generated by Django 3.1.1 on 2020-09-14 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0081_auto_20200821_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='gl_url',
            field=models.URLField(blank=True, help_text='HT__GITLAB_URL', verbose_name='VN__GITLAB_URL'),
        ),
        migrations.AlterField(
            model_name='mergerequest',
            name='gl_url',
            field=models.URLField(blank=True, help_text='HT__GITLAB_URL', verbose_name='VN__GITLAB_URL'),
        ),
        migrations.AlterField(
            model_name='milestone',
            name='gl_url',
            field=models.URLField(blank=True, help_text='HT__GITLAB_URL', verbose_name='VN__GITLAB_URL'),
        ),
        migrations.AlterField(
            model_name='project',
            name='gl_url',
            field=models.URLField(blank=True, help_text='HT__GITLAB_URL', verbose_name='VN__GITLAB_URL'),
        ),
        migrations.AlterField(
            model_name='projectgroup',
            name='gl_url',
            field=models.URLField(blank=True, help_text='HT__GITLAB_URL', verbose_name='VN__GITLAB_URL'),
        ),
    ]
