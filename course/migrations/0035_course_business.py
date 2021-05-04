# Generated by Django 2.2.19 on 2021-05-02 21:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0002_auto_20210502_0028'),
        ('course', '0034_enrollment_invite_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='business',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='onboarding.Business'),
        ),
    ]