# Generated by Django 2.2.5 on 2019-10-29 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0016_auto_20191017_1838"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(blank=True, default="", help_text="HT__EMAIL", max_length=150, verbose_name="VN__EMAIL"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="gl_avatar",
            field=models.URLField(blank=True, default="", help_text="HT__GITLAB_AVATAR", verbose_name="VN__GITLAB_AVATAR"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="gl_url",
            field=models.URLField(blank=True, default="", help_text="HT__GITLAB_URL", verbose_name="VN__GITLAB_URL"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="login",
            field=models.CharField(blank=True, default="", help_text="HT__LOGIN", max_length=150, unique=True, verbose_name="VN__LOGIN"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="name",
            field=models.CharField(blank=True, default="", help_text="HT__NAME", max_length=150, verbose_name="VN__NAME"),
            preserve_default=False,
        ),
    ]
