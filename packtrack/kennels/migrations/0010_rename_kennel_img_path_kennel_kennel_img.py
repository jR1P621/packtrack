# Generated by Django 4.0.2 on 2022-02-27 20:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kennels', '0009_alter_kennel_kennel_members'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kennel',
            old_name='kennel_img_path',
            new_name='kennel_img',
        ),
    ]