# Generated by Django 2.2.10 on 2020-02-18 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0023_course_is_confirmed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='day_of_week',
            field=models.CharField(choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], max_length=9),
        ),
    ]
