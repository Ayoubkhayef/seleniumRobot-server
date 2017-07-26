# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-26 19:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('snapshotServer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StepResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.BooleanField()),
                ('stacktrace', models.TextField(null=True)),
                ('step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stepresult', to='snapshotServer.TestStep')),
            ],
        ),
        migrations.AddField(
            model_name='testcaseinsession',
            name='stacktrace',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='stepresult',
            name='testCase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stepresult', to='snapshotServer.TestCaseInSession'),
        ),
    ]
