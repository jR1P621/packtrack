# Generated by Django 4.0.2 on 2022-03-13 21:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_attend_claimants_alter_attendclaim_claimant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='kennels',
        ),
        migrations.AlterField(
            model_name='longevity',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kennels', to='events.event'),
        ),
    ]