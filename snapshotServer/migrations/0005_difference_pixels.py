# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-05 19:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snapshotServer', '0004_auto_20170405_1857'),
    ]

    operations = [
        migrations.AddField(
            model_name='difference',
            name='pixels',
            field=models.BinaryField(null=True),
        ),
    ]
