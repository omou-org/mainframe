# Generated by Django 2.2.3 on 2020-01-27 01:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("invoice", "0002_auto_20200102_0245"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="attendance_start_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
