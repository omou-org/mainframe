# Generated by Django 2.2.19 on 2021-06-25 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pricing", "0018_auto_20210603_2215"),
    ]

    operations = [
        migrations.AddField(
            model_name="tuitionrule",
            name="retired",
            field=models.BooleanField(default=False),
        ),
    ]