# Generated by Django 2.2.19 on 2021-06-25 17:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pricing", "0019_tuitionrule_retired"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tuitionprice",
            name="is_retired",
        ),
    ]