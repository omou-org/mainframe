# Generated by Django 2.2.19 on 2021-02-21 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0009_auto_20201129_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='payment_status',
            field=models.CharField(choices=[('paid', 'Paid'), ('unpaid', 'Unpaid'), ('canceled', 'Canceled')], max_length=20),
        ),
    ]
