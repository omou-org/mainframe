# Generated by Django 2.2.20 on 2021-06-21 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding", "0002_auto_20210502_0028"),
    ]

    operations = [
        migrations.AddField(
            model_name="business",
            name="stripe_account_id",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
