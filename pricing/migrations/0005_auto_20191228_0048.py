# Generated by Django 2.2.8 on 2019-12-28 00:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pricing", "0004_delete_fee"),
    ]

    operations = [
        migrations.RenameField(
            model_name="multicoursediscount",
            old_name="num_classes",
            new_name="num_sessions",
        ),
        migrations.RemoveField(
            model_name="multicoursediscount",
            name="num_accounts",
        ),
    ]
