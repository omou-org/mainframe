# Generated by Django 2.2.3 on 2020-01-01 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0024_instructoravailability"),
    ]

    operations = [
        migrations.AlterField(
            model_name="admin",
            name="account_type",
            field=models.CharField(
                choices=[
                    ("student", "Student"),
                    ("parent", "Parent"),
                    ("instructor", "Instructor"),
                    ("admin", "Admin"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="admin",
            name="admin_type",
            field=models.CharField(
                choices=[
                    ("owner", "Owner"),
                    ("receptionist", "Receptionist"),
                    ("assisstant", "Assisstant"),
                ],
                max_length=20,
            ),
        ),
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
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="instructor",
            name="account_type",
            field=models.CharField(
                choices=[
                    ("student", "Student"),
                    ("parent", "Parent"),
                    ("instructor", "Instructor"),
                    ("admin", "Admin"),
                ],
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
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="parent",
            name="account_type",
            field=models.CharField(
                choices=[
                    ("student", "Student"),
                    ("parent", "Parent"),
                    ("instructor", "Instructor"),
                    ("admin", "Admin"),
                ],
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
                max_length=1,
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
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="student",
            name="account_type",
            field=models.CharField(
                choices=[
                    ("student", "Student"),
                    ("parent", "Parent"),
                    ("instructor", "Instructor"),
                    ("admin", "Admin"),
                ],
                max_length=20,
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
                max_length=1,
            ),
        ),
    ]
