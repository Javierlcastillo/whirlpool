# Generated by Django 5.1.7 on 2025-04-03 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_course_region'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='duration_weeks',
        ),
        migrations.AddField(
            model_name='course',
            name='duration_hours',
            field=models.PositiveSmallIntegerField(default=8, verbose_name='Duración (horas)'),
        ),
    ]
