# Generated by Django 4.0.2 on 2022-03-11 03:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kennels', '0007_alter_consensusvote_vote'),
        ('events', '0002_rename_event_date_event_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alt_name', models.CharField(max_length=64, null=True)),
                ('is_hare', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance', to='events.event')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attendance', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Longevity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('kennel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kennels.kennel')),
            ],
        ),
        migrations.CreateModel(
            name='LongevityRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_longevity', models.BooleanField(default=True)),
                ('attend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='longevity_records', to='events.attend')),
                ('longevity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.longevity')),
            ],
        ),
        migrations.AddConstraint(
            model_name='longevityrecord',
            constraint=models.UniqueConstraint(fields=('attend', 'longevity'), name='unique_longevity_record'),
        ),
        migrations.AddConstraint(
            model_name='longevity',
            constraint=models.UniqueConstraint(fields=('event', 'kennel'), name='unique_longevity'),
        ),
        migrations.AddConstraint(
            model_name='attend',
            constraint=models.CheckConstraint(check=models.Q(('alt_name__isnull', True)), name='attend_not_claimed_and_unclaimed'),
        ),
        migrations.AddConstraint(
            model_name='attend',
            constraint=models.UniqueConstraint(condition=models.Q(('alt_name__isnull', True)), fields=('event', 'user'), name='unique_claimed_attend'),
        ),
        migrations.AddConstraint(
            model_name='attend',
            constraint=models.UniqueConstraint(condition=models.Q(('user__isnull', True)), fields=('event', 'alt_name'), name='unique_unclaimed_attend'),
        ),
    ]