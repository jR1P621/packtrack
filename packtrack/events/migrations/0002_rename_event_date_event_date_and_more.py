# Generated by Django 4.0.2 on 2022-03-11 02:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kennels', '0007_alter_consensusvote_vote'),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='event_date',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='event_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='event',
            name='event_desc',
        ),
        migrations.AddField(
            model_name='event',
            name='host',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='kennels.kennel'),
            preserve_default=False,
        ),
    ]
