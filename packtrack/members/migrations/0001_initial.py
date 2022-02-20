# Generated by Django 4.0.2 on 2022-02-19 19:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kennels', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_avatar', models.ImageField(null=True, upload_to='')),
                ('member_hash_name', models.CharField(max_length=64)),
                ('member_email', models.EmailField(max_length=254, null=True)),
                ('member_user_account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MemberURLs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('url_desc', models.CharField(max_length=32)),
                ('url_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.member')),
            ],
        ),
        migrations.CreateModel(
            name='MembershipRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_kennel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kennels.kennel')),
                ('request_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.member')),
            ],
        ),
        migrations.CreateModel(
            name='InviteCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invite_code', models.CharField(max_length=8)),
                ('invite_expiration', models.DateField()),
                ('invite_creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invite_creator', to='members.member')),
                ('invite_receiver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invite_receiver', to='members.member')),
            ],
        ),
    ]