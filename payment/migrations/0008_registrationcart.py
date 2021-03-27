# Generated by Django 2.2.12 on 2020-07-25 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0040_auto_20200722_0128'),
        ('payment', '0007_deduction'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_preferences', models.TextField()),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Parent')),
            ],
        ),
    ]