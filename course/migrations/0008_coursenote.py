# Generated by Django 2.2.7 on 2019-11-13 06:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("course", "0007_auto_20191110_2050"),
    ]

    operations = [
        migrations.CreateModel(
            name="CourseNote",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("title", models.TextField(blank=True)),
                ("body", models.TextField()),
                ("important", models.BooleanField(default=False)),
                ("complete", models.BooleanField(default=False)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="course.Course"
                    ),
                ),
            ],
        ),
    ]
