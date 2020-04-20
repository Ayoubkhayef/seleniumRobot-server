# Generated by Django 3.0.4 on 2020-04-20 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snapshotServer', '0005_auto_20200408_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='snapshot',
            name='diffTolerance',
            field=models.IntegerField(default=0),
        ),
        migrations.AddConstraint(
            model_name='snapshot',
            constraint=models.CheckConstraint(check=models.Q(('diffTolerance__gte', 0), ('diffTolerance__lte', 100)), name='percentage_diff_tolerance'),
        ),
    ]
