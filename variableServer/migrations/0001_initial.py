# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-25 08:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('snapshotServer', '0005_testenvironment_genericenvironment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=300)),
                ('releaseDate', models.DateTimeField(null=True)),
                ('internal', models.BooleanField(default=False)),
                ('protected', models.BooleanField(default=False)),
                ('description', models.CharField(default='', max_length=500, null=True)),
                ('application', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='snapshotServer.Application')),
                ('environment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='snapshotServer.TestEnvironment')),
                ('test', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='snapshotServer.TestCase')),
                ('version', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='snapshotServer.Version')),
            ],
            options={
                'permissions': (('see_protected_var', 'Can see protected vars'),),
            },
        ),
    ]
