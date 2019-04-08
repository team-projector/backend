# Generated by Django 2.1.7 on 2019-04-05 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0029_auto_20190404_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='gl_id',
            field=models.PositiveIntegerField(help_text='HT__GITLAB_ID', unique=True, verbose_name='VN__GITLAB_ID'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='gl_url',
            field=models.URLField(help_text='HT__GITLAB_URL', unique=True, verbose_name='VN__GITLAB_URL'),
        ),
        migrations.AlterField(
            model_name='milestone',
            name='gl_id',
            field=models.PositiveIntegerField(help_text='HT__GITLAB_ID', unique=True, verbose_name='VN__GITLAB_ID'),
        ),
        migrations.AlterField(
            model_name='milestone',
            name='gl_url',
            field=models.URLField(help_text='HT__GITLAB_URL', unique=True, verbose_name='VN__GITLAB_URL'),
        ),
        migrations.AlterField(
            model_name='project',
            name='gl_id',
            field=models.PositiveIntegerField(help_text='HT__GITLAB_ID', unique=True, verbose_name='VN__GITLAB_ID'),
        ),
        migrations.AlterField(
            model_name='project',
            name='gl_url',
            field=models.URLField(help_text='HT__GITLAB_URL', unique=True, verbose_name='VN__GITLAB_URL'),
        ),
        migrations.AlterField(
            model_name='projectgroup',
            name='gl_id',
            field=models.PositiveIntegerField(help_text='HT__GITLAB_ID', unique=True, verbose_name='VN__GITLAB_ID'),
        ),
        migrations.AlterField(
            model_name='projectgroup',
            name='gl_url',
            field=models.URLField(help_text='HT__GITLAB_URL', unique=True, verbose_name='VN__GITLAB_URL'),
        ),
    ]
