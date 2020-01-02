# Generated by Django 2.2.7 on 2020-01-02 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0021_auto_20200102_0706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='academic_level',
            field=models.CharField(choices=[('elementary_lvl', 'Elementary'), ('middle_lvl', 'Middle'), ('high_lvl', 'High'), ('college_lvl', 'College')], default='elementary_lvl', max_length=20),
        ),
        migrations.AlterField(
            model_name='course',
            name='course_type',
            field=models.CharField(choices=[('tutoring', 'Tutoring'), ('small_group', 'Small group'), ('class', 'Class')], default='tutoring', max_length=20),
        ),
    ]
