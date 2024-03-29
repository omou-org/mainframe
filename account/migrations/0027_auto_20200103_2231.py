# Generated by Django 2.2.9 on 2020-01-03 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0026_auto_20200101_2206"),
    ]

    operations = [
        migrations.AddField(
            model_name="instructor",
            name="biography",
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name="instructor",
            name="experience",
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name="instructor",
            name="languages",
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name="instructor",
            name="subjects",
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
