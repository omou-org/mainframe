# Generated by Django 2.2.3 on 2020-01-01 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0025_auto_20200101_1221"),
    ]

    operations = [
        migrations.AlterField(
            model_name="admin",
            name="gender",
            field=models.CharField(
                choices=[
                    ("male", "Male"),
                    ("female", "Female"),
                    ("unspecified", "Unspecified"),
                ],
                default="unspecified",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="instructor",
            name="gender",
            field=models.CharField(
                choices=[
                    ("male", "Male"),
                    ("female", "Female"),
                    ("unspecified", "Unspecified"),
                ],
                default="unspecified",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="parent",
            name="gender",
            field=models.CharField(
                choices=[
                    ("male", "Male"),
                    ("female", "Female"),
                    ("unspecified", "Unspecified"),
                ],
                default="unspecified",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="parent",
            name="relationship",
            field=models.CharField(
                blank=True,
                choices=[
                    ("mother", "Mother"),
                    ("father", "Father"),
                    ("guardian", "Guardian"),
                    ("other", "Other"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="gender",
            field=models.CharField(
                choices=[
                    ("male", "Male"),
                    ("female", "Female"),
                    ("unspecified", "Unspecified"),
                ],
                default="unspecified",
                max_length=20,
            ),
        ),
    ]
