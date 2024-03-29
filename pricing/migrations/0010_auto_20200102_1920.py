# Generated by Django 2.2.7 on 2020-01-02 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pricing", "0009_auto_20191228_0520"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pricerule",
            name="academic_level",
            field=models.CharField(
                choices=[
                    ("E", "Elementary"),
                    ("M", "Middle"),
                    ("H", "High"),
                    ("C", "College"),
                ],
                default="E",
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="pricerule",
            name="course_type",
            field=models.CharField(
                choices=[("T", "Tutoring"), ("S", "Small group"), ("C", "Class")],
                default="T",
                max_length=1,
            ),
        ),
    ]
