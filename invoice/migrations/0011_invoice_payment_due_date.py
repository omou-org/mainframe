# Generated by Django 2.2.20 on 2021-06-03 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoice", "0010_auto_20210221_0420"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="payment_due_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
