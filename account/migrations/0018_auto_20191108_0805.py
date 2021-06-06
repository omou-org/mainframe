# Generated by Django 2.2.3 on 2019-11-08 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0017_auto_20191029_0706"),
    ]

    operations = [
        migrations.AlterField(
            model_name="parent",
            name="relationship",
            field=models.CharField(
                blank=True,
                choices=[
                    ("MOTHER", "Mother"),
                    ("FATHER", "Father"),
                    ("GUARDIAN", "Guardian"),
                    ("OTHER", "Other"),
                ],
                max_length=10,
                null=True,
            ),
        ),
    ]
