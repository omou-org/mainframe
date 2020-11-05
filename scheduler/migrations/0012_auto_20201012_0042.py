# Generated by Django 2.2.14 on 2020-10-12 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0011_auto_20201012_0041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('', ''), ('present', 'Present'), ('tardy', 'Tardy'), ('absent', 'Absent')], default='', max_length=7),
        ),
    ]
