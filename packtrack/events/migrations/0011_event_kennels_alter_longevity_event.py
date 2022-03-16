# Generated by Django 4.0.2 on 2022-03-13 21:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kennels', '0014_remove_consensus_consensus_type_constraint_and_more'),
        ('events', '0010_remove_event_kennels_alter_longevity_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='kennels',
            field=models.ManyToManyField(through='events.Longevity', to='kennels.Kennel'),
        ),
        migrations.AlterField(
            model_name='longevity',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event'),
        ),
    ]