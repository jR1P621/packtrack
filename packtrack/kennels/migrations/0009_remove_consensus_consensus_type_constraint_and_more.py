# Generated by Django 4.0.2 on 2022-03-13 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kennels', '0008_remove_consensus_unique_consensus_consensus_event_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='consensus',
            name='consensus_type_constraint',
        ),
        migrations.AddConstraint(
            model_name='consensus',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('event__isnull', True), ('member__isnull', False), ('type__in', [0, 1, 2])), models.Q(('event__isnull', False), ('member__isnull', True), ('type__in', [3, 4])), _connector='OR'), name='consensus_type_constraint'),
        ),
    ]