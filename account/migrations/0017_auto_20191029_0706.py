# Generated by Django 2.2.3 on 2019-10-29 07:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0016_auto_20191029_0701"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="grade",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(13),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="school",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
