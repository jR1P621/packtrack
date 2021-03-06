# Generated by Django 4.0.2 on 2022-03-07 04:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Consensus',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     serialize=False,
                                     verbose_name='ID')),
                ('result', models.FloatField(blank=True, null=True)),
                ('action', models.CharField(max_length=128)),
                ('initiator',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='Kennel',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     serialize=False,
                                     verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('acronym', models.CharField(default='', max_length=16)),
                ('city', models.CharField(max_length=128, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('image', models.ImageField(null=True, upload_to='')),
                ('about', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     serialize=False,
                                     verbose_name='ID')),
                ('is_approved', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('kennel',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='kennels.kennel')),
                ('user',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='kennel',
            name='members',
            field=models.ManyToManyField(related_name='kennels',
                                         through='kennels.Membership',
                                         to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ConsensusVote',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     serialize=False,
                                     verbose_name='ID')),
                ('vote', models.BooleanField()),
                ('consensus',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='kennels.consensus')),
                ('voter',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='consensus',
            name='kennel',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='kennels.kennel'),
        ),
        migrations.AddField(
            model_name='consensus',
            name='polymorphic_ctype',
            field=models.ForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='polymorphic_%(app_label)s.%(class)s_set+',
                to='contenttypes.contenttype'),
        ),
        migrations.AddConstraint(
            model_name='membership',
            constraint=models.UniqueConstraint(fields=('user', 'kennel'),
                                               name='unique_membership'),
        ),
    ]
