# Generated by Django 2.2.12 on 2020-07-03 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduler", "0005_session_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="session",
            name="sent_reminder",
            field=models.BooleanField(default=False),
        ),
    ]
