# Generated by Django 2.2.3 on 2019-11-15 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0020_auto_20191114_0843"),
    ]

    operations = [
        migrations.AlterField(
            model_name="instructor",
            name="age",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
