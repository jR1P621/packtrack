# Generated by Django 4.0.2 on 2022-02-26 02:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0007_remove_member_member_kennels_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitecode',
            name='invite_expiration',
            field=models.DateField(default=datetime.date(2022, 3, 5), null=True),
        ),
    ]
