# Generated by Django 3.2.18 on 2024-03-06 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snapshotServer', '0024_testinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='testsession',
            name='startedBy',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
