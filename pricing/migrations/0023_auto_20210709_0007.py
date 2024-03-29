# Generated by Django 2.2.23 on 2021-07-09 00:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course", "0035_course_business"),
        ("pricing", "0022_auto_20210708_2158"),
    ]

    operations = [
        migrations.RenameField(
            model_name="discount",
            old_name="name",
            new_name="code",
        ),
        migrations.RemoveField(
            model_name="discount",
            name="description",
        ),
        migrations.AddField(
            model_name="discount",
            name="all_courses_apply",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="discount",
            name="auto_apply",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="discount",
            name="courses",
            field=models.ManyToManyField(blank=True, to="course.Course"),
        ),
        migrations.AddField(
            model_name="discount",
            name="end_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="discount",
            name="min_courses",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(2),
                    django.core.validators.MaxValueValidator(1000),
                ],
            ),
        ),
        migrations.AddField(
            model_name="discount",
            name="payment_method",
            field=models.CharField(
                blank=True,
                choices=[
                    ("cash", "Cash"),
                    ("course_credit", "Course Credit"),
                    ("credit_card", "Credit Card"),
                    ("check", "Check"),
                    ("intl_credit_card", "International Credit Card"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="discount",
            name="start_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
