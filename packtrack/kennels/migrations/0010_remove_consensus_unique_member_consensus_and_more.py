# Generated by Django 4.0.2 on 2022-03-13 20:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kennels',
         '0009_remove_consensus_consensus_type_constraint_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='consensus',
            name='unique_member_consensus',
        ),
        migrations.RemoveConstraint(
            model_name='consensus',
            name='consensus_type_constraint',
        ),
        migrations.RemoveField(
            model_name='consensus',
            name='member',
        ),
        migrations.AddField(
            model_name='consensus',
            name='membership',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='consensus',
                to='kennels.membership'),
        ),
    ]
