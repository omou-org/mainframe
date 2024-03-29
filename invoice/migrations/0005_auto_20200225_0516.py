# Generated by Django 2.2.7 on 2020-02-25 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoice", "0004_auto_20200210_0025"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="account_balance",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
        migrations.AddField(
            model_name="payment",
            name="discount_total",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
    ]
