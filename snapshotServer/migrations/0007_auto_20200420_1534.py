# Generated by Django 3.0.4 on 2020-04-20 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snapshotServer', '0006_auto_20200420_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snapshot',
            name='diffTolerance',
            field=models.FloatField(default=0.0),
        ),
    ]
