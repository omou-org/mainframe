# Generated by Django 2.2.3 on 2019-07-28 19:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("course", "0004_auto_20190722_0313"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="course_category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="course.CourseCategory",
            ),
        ),
    ]
