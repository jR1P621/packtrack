# Generated by Django 4.0.2 on 2022-02-28 05:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0012_alter_invitecode_invite_expiration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitecode',
            name='invite_expiration',
            field=models.DateField(default=datetime.date(2022, 3, 7), null=True),
        ),
    ]
