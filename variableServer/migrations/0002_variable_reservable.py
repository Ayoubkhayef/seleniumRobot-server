# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-06 15:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('variableServer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='reservable',
            field=models.BooleanField(default=False),
        ),
    ]
