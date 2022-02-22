# Generated by Django 4.0.2 on 2022-02-21 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kennels', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kennel',
            name='kennel_abbr',
            field=models.CharField(default='', max_length=16),
        ),
        migrations.AlterField(
            model_name='kennel',
            name='kennel_name',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
