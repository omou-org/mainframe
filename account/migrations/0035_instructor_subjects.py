# Generated by Django 2.2.10 on 2020-03-27 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course", "0025_optional_day_of_week"),
        ("account", "0034_instructoroutofoffice_description"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="instructor",
            name="subjects",
        ),
        migrations.AddField(
            model_name="instructor",
            name="subjects",
            field=models.ManyToManyField(blank=True, to="course.CourseCategory"),
        ),
    ]
