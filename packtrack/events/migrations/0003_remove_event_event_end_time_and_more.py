# Generated by Django 4.0.2 on 2022-02-23 19:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='event_end_time',
        ),
        migrations.RemoveField(
            model_name='event',
            name='event_start_time',
        ),
    ]
