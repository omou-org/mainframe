# Generated by Django 2.2.14 on 2021-03-27 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0010_attendance'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='sent_missed_reminder',
            field=models.BooleanField(default=False),
        ),
    ]
