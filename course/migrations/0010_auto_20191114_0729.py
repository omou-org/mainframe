# Generated by Django 2.2.3 on 2019-11-14 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course", "0009_enrollmentnote"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="day_of_week",
            field=models.CharField(max_length=27),
        ),
    ]
