from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0045_auto_20190514_2347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='Issue',
            name='feature',
            field=models.IntegerField(),
        ),
    ]
