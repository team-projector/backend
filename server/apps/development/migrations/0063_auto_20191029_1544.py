# Generated by Django 2.2.5 on 2019-10-29 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("development", "0062_auto_20191028_1543"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="is_archived",
            field=models.BooleanField(default=False, help_text="HT__IS_ARCHIVED", verbose_name="VN__IS_ARCHIVED"),
        ),
    ]
