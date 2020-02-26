# Generated by Django 2.2.10 on 2020-02-18 01:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0030_parent_balance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instructoravailability',
            name='friday_end_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='friday_start_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='monday_end_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='monday_start_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='saturday_end_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='saturday_start_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='sunday_end_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='sunday_start_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='thursday_end_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='thursday_start_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='tuesday_end_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='tuesday_start_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='wednesday_end_time',
        ),
        migrations.RemoveField(
            model_name='instructoravailability',
            name='wednesday_start_time',
        ),
        migrations.AddField(
            model_name='instructoravailability',
            name='day_of_week',
            field=models.CharField(choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], default='monday', max_length=9),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instructoravailability',
            name='end_time',
            field=models.TimeField(default=datetime.time(1, 49, 4, 685230)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instructoravailability',
            name='start_time',
            field=models.TimeField(default=datetime.time(1, 49, 32, 357843)),
            preserve_default=False,
        ),
    ]